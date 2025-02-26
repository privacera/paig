import asyncio
import json
import traceback
import uuid
from api.evaluation.database.db_operations.eval_config_repository import EvaluationConfigHistoryRepository
from api.evaluation.database.db_operations.eval_target_repository import EvaluationTargetRepository
from core.utils import SingletonDepends
from api.evaluation.database.db_operations.eval_repository import EvaluationRepository
from paig_evaluation.paig_evaluator import PAIGEvaluator, get_suggested_plugins, get_all_plugins
from paig_evaluation.promptfoo_utils import ensure_promptfoo_config
import logging
from core.utils import current_utc_time
from core.exceptions import BadRequestException

logger = logging.getLogger(__name__)


from core.db_session.transactional import Transactional, Propagation
from core.db_session.standalone_session import update_table_fields, bulk_insert_into_table

ensure_promptfoo_config('promptfoo@paig.ai')



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
        "create_time": current_utc_time()
    }

async def insert_eval_results(eval_id, eval_run_id, report):
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
            "response": res['response']['output'] if 'response' in res else 'NA',
            "failure_reason": res['error'] if res['failureReason'] else None,
            "category_score": json.dumps(res['namedScores']),
            "status": 'PASSED' if res['success'] else 'FAILED'
        }  # Add prompt_id in response
        if res['failureReason'] == 2:
            response['status'] = 'ERROR'
        if 'testCase' in res and 'metadata' in res['testCase'] and 'pluginId' in res['testCase']['metadata']:
            response['category'] = res['testCase']['metadata']['pluginId']
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
                generated_prompts_config_result = eval_obj.generate_prompts(application_config=application_config, plugins=categories, targets=target_hosts)
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
            verbose=False
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

    async def get_target_hosts(self, apps):
        final_target = list()
        app_names = list()
        for app in apps:
            target_host = json.loads(app.config)
            if 'headers'in target_host['config'] and target_host['config']['headers'] == {}:
                del target_host['config']['headers']
            target_host['label'] = app.name
            app_names.append(app.name)
            final_target.append(target_host)
        return final_target, app_names

    @Transactional(propagation=Propagation.REQUIRED)
    async def run_evaluation(self, eval_config_id, owner, base_run_id=None, report_name=None):
        eval_config = await self.eval_config_history_repository.get_eval_config_by_config_id(eval_config_id)
        if eval_config is None:
            raise BadRequestException('Configuration does not exists')
        app_ids = [int(app_id) for app_id in (eval_config.application_ids).split(',') if app_id.strip()]
        apps = await self.eval_target_repository.get_applications_by_in_list('id', app_ids)
        if len(apps) != len(app_ids):
            raise BadRequestException('Applications are not configured properly.Please check the configuration')
        target_hosts, application_names = await self.get_target_hosts(apps)
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
            "name": report_name
        }
        eval_model= await self.evaluation_repository.create_new_evaluation(eval_params)
        eval_run_id = eval_model.id
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
        suggested_categories = get_suggested_plugins(purpose)
        if not isinstance(suggested_categories, dict):
            raise BadRequestException('Invalid response received for for suggested categories')
        if suggested_categories['status'] != 'success':
            raise BadRequestException(suggested_categories['message'])
        resp['suggested_categories'] = suggested_categories['result']
        all_categories = get_all_plugins()
        if not isinstance(all_categories, dict):
            raise BadRequestException('Invalid response received for for all categories')
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