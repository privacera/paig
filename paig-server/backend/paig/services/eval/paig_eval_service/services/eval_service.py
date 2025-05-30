import asyncio
import json
import os
import traceback
import uuid

from ..database.db_operations.eval_config_repository import EvaluationConfigHistoryRepository
from ..database.db_operations.eval_target_repository import EvaluationTargetRepository
from core.utils import SingletonDepends
from ..database.db_operations.eval_repository import EvaluationRepository
from paig_evaluation.paig_evaluator import PAIGEvaluator, get_suggested_plugins, get_all_plugins, eval_init_config
from paig_evaluation.promptfoo_utils import get_security_plugin_map
import logging
from core.utils import current_utc_time, replace_timezone
from core.exceptions import BadRequestException, TooManyRequestsException
from core.config import load_config_file


config = load_config_file()
logger = logging.getLogger(__name__)


from core.db_session.transactional import Transactional, Propagation
from core.db_session.standalone_session import update_table_fields, bulk_insert_into_table
from core.middlewares.request_session_context_middleware import get_tenant_id
from ..utility import decrypt_target_creds

if config.get("disable_remote_eval_plugins", False):
    # Disable remote eval plugins if the config is set
    logger.info(f"setting remote eval plugins to {config.get('disable_remote_eval_plugins')}")
    os.environ['PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION'] = str(config.get("disable_remote_eval_plugins"))
model = config.get("llm", {}).get("model") or "gpt-4"

eval_init_config(
    email='promptfoo@paig.ai',
    plugin_file_path=config.get("eval_category_file", None),
    model=model,
)

DISABLE_EVAL_CONCURRENT_LIMIT = str(config.get("disable_eval_concurrent_limit", "false")).lower() == "true"
MAX_CONCURRENT_EVALS = config.get("max_eval_concurrent_limit", 2)
EVAL_TIMEOUT = config.get("eval_timeout_in_min", 6*60) # 6 hours
ENABLE_EVAL_VERBOSE = str(config.get("enable_eval_verbose", "false")).lower() == "true"

def prepare_report_format(result, update_eval_params):
    results = result["results"]
    cumulative_result = results['prompts']
    update_eval_params['status'] = 'COMPLETED'
    update_eval_params['update_time'] = current_utc_time()
    update_eval_params['cumulative_result'] = json.dumps(cumulative_result)
    # update pass counts
    total_passed = list()
    total_failed = list()
    for metric in cumulative_result:
        metrics = metric['metrics']
        total_passed.append(str(metrics['testPassCount']))
        total_failed.append(str(metrics['testFailCount'] + metrics['testErrorCount']))
    update_eval_params['passed'] = ', '.join(total_passed)
    update_eval_params['failed'] = ', '.join(total_failed)
    return update_eval_params

def generate_common_fields(eval_run_id, eval_id):
    return {
        "eval_run_id": eval_run_id,
        "eval_id": eval_id.strip(),
        "create_time": current_utc_time(),
        "tenant_id": get_tenant_id()
    }

async def insert_eval_results(eval_id, eval_run_id, report):
    all_plugins_info = get_security_plugin_map()
    results = report["result"]
    if 'results' not in results:
        logger.info(f'No result is generated for eval_id: {eval_id}')
        return
    results = results["results"]
    results = results["results"]
    prompt_records = list()
    response_records = list()
    # Set to keep track of processed prompt testIdx values
    processed_test_idxs = set()

    # Dictionary to store generated IDs for each prompt
    prompt_id_map = {}

    for res in results:
        test_idx = res['testIdx']
        # Generate the common fields
        common_fields = generate_common_fields(eval_run_id, eval_id)
        # If the testIdx has not been processed before, insert the prompt and generate a new ID
        if test_idx not in processed_test_idxs:
            new_prompt_id = str(uuid.uuid4())  # Generate a new unique ID for the prompt
            prompt = {
                **common_fields,
                "prompt_uuid": new_prompt_id,
                "prompt": res['prompt']['raw']
            }
            prompt_records.append(prompt)
            prompt_id_map[test_idx] = new_prompt_id  # Map testIdx to new prompt ID
            processed_test_idxs.add(test_idx)
            # Insert the response and link it to the prompt using the generated ID
        response = {
            **common_fields,
            "eval_result_prompt_uuid": prompt_id_map[test_idx],
            "application_name": res['provider']['label'],
            "response": res['response']['output'] if 'response' in res and 'output' in res['response'] else 'NA',
            "failure_reason": res['error'] if (res['failureReason'] or  not res['success']) and 'error' in res  else None,
            "category_score": json.dumps(res['namedScores']),
            "status": 'PASSED' if res['success'] else 'FAILED',
            "category_severity": None,
            "category_type": None
        }  # Add prompt_id in response
        if res['failureReason'] == 2:
            response['status'] = 'ERROR'
        if 'testCase' in res and 'metadata' in res['testCase'] and 'pluginId' in res['testCase']['metadata']:
            category = res['testCase']['metadata']['pluginId']
            response['category'] = category
            response['category_type'] = all_plugins_info.get(category, {}).get('type', 'Custom')
            if response['status'] != 'PASSED':
                response['category_severity'] = all_plugins_info.get(category, {}).get('severity', 'LOW')
        response_records.append(response)
    # Insert the prompt and response records
    await bulk_insert_into_table('eval_result_prompt', prompt_records)
    await bulk_insert_into_table('eval_result_response', response_records)
    return



def threaded_run_evaluation(eval_id, eval_run_id, eval_config, target_hosts, application_names):
    async def async_operations():
        # Update config in database
        update_eval_params = dict()
        static_prompts = eval_config.custom_prompts
        if static_prompts != '' and isinstance(static_prompts, str):
            static_prompts = json.loads(static_prompts)
        categories = eval_config.categories
        if categories != '' and isinstance(categories, str):
            categories = json.loads(categories)
        # Create application configuration
        application_config = {
            "paig_eval_id": eval_id,
            "application_name": ','.join(application_names),
            "purpose": eval_config.purpose,
        }
        eval_obj = PAIGEvaluator()
        generated_prompts_config = dict()
        if not eval_config.generated_config:
            try:
                generated_prompts_config_result = eval_obj.generate_prompts(application_config=application_config, plugins=categories, targets=target_hosts, verbose=ENABLE_EVAL_VERBOSE)
                if generated_prompts_config_result['status'] != 'success':
                    update_eval_params['status'] = 'FAILED'
                    logger.error('Prompts generation failed:- ' + str(generated_prompts_config_result['message']))
                else:
                    update_eval_params['status'] = 'EVALUATING'
                    generated_prompts_config = generated_prompts_config_result['result']
                    eval_config_params = {
                        'generated_config': json.dumps(generated_prompts_config)
                    }
                    await update_table_fields('eval_config_history', eval_config_params, 'eval_config_id', eval_config.id)
                    logger.info('Prompts generation completed')
            except Exception as err:
                logger.error('Error: ' + str(err))
                logger.error(str(traceback.print_exc()))
                update_eval_params['status'] = 'FAILED'
            finally:
                await update_table_fields('eval_run', update_eval_params, 'eval_id', eval_id)
        else:
            generated_prompts_config = json.loads(eval_config.generated_config)
            logger.info('Prompts already generated')
        if 'status' in update_eval_params and update_eval_params['status'] == 'FAILED':
            logger.info('Generation failed. Skipping evaluation')
            return
        logger.info('Proceeding to evaluate')
        # Append static custom prompts
        user_prompts_list = []
        if isinstance(static_prompts, list) and len(static_prompts) > 0:
            for prompt in static_prompts:
                if prompt['prompt'] and prompt['criteria']:
                    prompt_obj = {
                        "vars": {"prompt": prompt['prompt']},
                        "assert": [{"type": "llm-rubric", "value": prompt['criteria']}]
                    }
                    user_prompts_list.append(prompt_obj)
        custom_prompts = {'tests': user_prompts_list}
        report = eval_obj.evaluate(
            paig_eval_id=eval_id,
            generated_prompts=generated_prompts_config,
            custom_prompts=custom_prompts,
            verbose= ENABLE_EVAL_VERBOSE
        )
        logger.info('Evaluation completed with status ' + str(report['status']))
        try:
            if report['status'] == 'success':
                update_eval_params = prepare_report_format(report['result'], update_eval_params)
            else:
                update_eval_params['status'] = 'FAILED'
                logger.error('Evaluation failed:- ' + str(report['message']))
            await update_table_fields('eval_run', update_eval_params, 'eval_id', eval_id)
            await insert_eval_results(eval_id, eval_run_id, report)
        except Exception as err:
            logger.error('Error while updating DB: ' + str(err))
            logger.error(str(traceback.print_exc()))
        return report

    # Run the async operations in a new event loop
    asyncio.run(async_operations())



class EvaluationService:

    def __init__(
        self,
        evaluation_repository: EvaluationRepository = SingletonDepends(EvaluationRepository),
        eval_config_history_repository: EvaluationConfigHistoryRepository = SingletonDepends(EvaluationConfigHistoryRepository),
        eval_target_repository: EvaluationTargetRepository = SingletonDepends(EvaluationTargetRepository)
    ):
        self.evaluation_repository = evaluation_repository
        self.eval_config_history_repository = eval_config_history_repository
        self.eval_target_repository = eval_target_repository

    def get_paig_evaluator(self):
        return PAIGEvaluator()

    async def get_target_hosts(self, apps, auth_user):
        final_target = list()
        app_names = list()
        target_users = list()
        for app in apps:
            target_host = json.loads(app.config)
            target_user = app.target_user
            if 'headers'in target_host['config']:
                if auth_user and str(app.id) in auth_user.keys():
                    headers = target_host['config']['headers']
                    existing_auth_key = next((key for key in headers.keys() if key.lower() == 'authorization'), None)
                    # Remove the old key if found
                    if existing_auth_key:
                        del headers[existing_auth_key]
                    headers['Authorization'] = auth_user[str(app.id)]['token']
                    target_user = auth_user[str(app.id)]['username']
                elif target_host['config']['headers'] == {}:
                    del target_host['config']['headers']
                else:
                    target_host['config']['headers'] = await decrypt_target_creds(target_host['config']['headers'])
            target_host['label'] = app.name
            app_names.append(app.name)
            final_target.append(target_host)
            target_users.append(target_user)
        return final_target, app_names, target_users

    @Transactional(propagation=Propagation.REQUIRED)
    async def run_evaluation(self, eval_config_id, owner, base_run_id=None, report_name=None, auth_user=None):
        if not await self.validate_eval_availability():
            raise TooManyRequestsException('The maximum number of evaluations has already been reached. Please try again once one has completed.')
        eval_config = await self.eval_config_history_repository.get_eval_config_by_config_id(eval_config_id)
        if eval_config is None:
            raise BadRequestException('Configuration does not exists')
        app_ids = [int(app_id) for app_id in (eval_config.application_ids).split(',') if app_id.strip()]
        apps = await self.eval_target_repository.get_applications_by_in_list('id', app_ids)
        if len(apps) != len(app_ids):
            raise BadRequestException('Applications are not configured properly.Please check the configuration')
        target_hosts, application_names, target_users = await self.get_target_hosts(apps, auth_user)
        # Insert evaluation record
        eval_id = str(uuid.uuid4())
        eval_params = {
            "status": "GENERATING",
            "config_id": eval_config_id,
            "owner": owner,
            "eval_id": eval_id,
            "purpose": eval_config.purpose,
            "config_name": eval_config.name,
            "application_names": ','.join(application_names),
            "base_run_id": base_run_id,
            "name": report_name,
            "target_users": ','.join(target_users)
        }
        eval_model= await self.evaluation_repository.create_new_evaluation(eval_params)
        eval_run_id = eval_model.id
        if base_run_id is None:
            eval_config.generated_config = None
        asyncio.create_task(
            asyncio.to_thread(
                threaded_run_evaluation,
                eval_id,
                eval_run_id,
                eval_config,
                target_hosts,
                application_names
            )
        )
        return

    async def delete_evaluation(self, eval_id: int):
        """
        Delete an AI application by its ID.

        Args:
            id (int): The ID of the AI application to delete.
        """
        existing_evaluation = await self.evaluation_repository.get_evaluations_by_field('id', eval_id)
        return await self.evaluation_repository.delete_evaluation(existing_evaluation)

    @staticmethod
    async def get_categories(purpose):
        resp = dict()

        # Get model from config here
        model = eval_config.get("llm", {}).get("model", "gpt-4")
        suggested_categories = get_suggested_plugins(purpose, model=model)
        if not isinstance(suggested_categories, dict):
            raise BadRequestException('Invalid response received for suggested categories')
        if suggested_categories['status'] != 'success':
            raise BadRequestException(suggested_categories['message'])
        resp['suggested_categories'] = suggested_categories['result']

        all_categories = get_all_plugins()
        if not isinstance(all_categories, dict):
            raise BadRequestException('Invalid response received for all categories')
        if all_categories['status'] != 'success':
            raise BadRequestException(all_categories['message'])
        resp['all_categories'] = all_categories['result']

        return resp


    async def rerun_evaluation_by_id(self, eval_id, owner, report_name):
        existing_evaluation = await self.evaluation_repository.get_evaluations_by_field('id', eval_id)
        if existing_evaluation is None:
            raise BadRequestException('Invalid evaluation ID')
        base_run_id = existing_evaluation.eval_id
        if existing_evaluation.base_run_id:
            base_run_id = existing_evaluation.base_run_id
        return await self.run_evaluation(existing_evaluation.config_id, owner, base_run_id=base_run_id, report_name=report_name)



    async def validate_eval_availability(self):
        """
        Validate if the evaluation is available.
        """
        if DISABLE_EVAL_CONCURRENT_LIMIT:
            return True
        active_existing_evaluation = await self.evaluation_repository.get_active_evaluation()
        if not active_existing_evaluation:
            return True
        active_evals = len(active_existing_evaluation)
        # Mark timeout evaluations as failed
        for evaluation in active_existing_evaluation:
            if evaluation.create_time and (current_utc_time() - replace_timezone(evaluation.create_time)).total_seconds() > EVAL_TIMEOUT * 60:
                logger.info(f"Evaluation timed out for eval_id: {evaluation.eval_id}")
                # Update the evaluation status to FAILED
                await self.evaluation_repository.update_evaluation({'status': 'FAILED'}, evaluation)
                active_evals -= 1
        return  active_evals < MAX_CONCURRENT_EVALS