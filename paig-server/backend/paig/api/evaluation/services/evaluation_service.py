import asyncio
import copy
import json
import traceback

from core.utils import SingletonDepends
from api.evaluation.database.db_operations.evaluation_repository import EvaluationRepository
from core.config import load_config_file
from paig_evaluation.paig_evaluator import PAIGEvaluator
import logging
from core.utils import current_utc_time, format_to_root_path
logger = logging.getLogger(__name__)
config = load_config_file()


from core.db_session.transactional import Transactional, Propagation
from core.db_session.standalone_session import update_table_fields

if 'evaluation_targets' in config:
    target_file = config['evaluation_targets']
else:
    target_file = format_to_root_path('conf/evaluation_targets.json')

with open(target_file, 'r') as f:
    targets = json.load(f)


def threaded_run_evaluation(evaluation_config, categories, static_prompts):
    async def async_operations():
        eval_id = evaluation_config['eval_id']
        # Update config in database
        update_eval_params = dict()
        proceed_to_eval = False
        print(evaluation_config['application_name'])
        if isinstance(evaluation_config['application_name'], str):
            evaluation_config['application_name'] = evaluation_config['application_name'].split(',')
        try:
            final_target = list()
            for app_name in evaluation_config['application_name']:
                if app_name in targets.keys():
                    final_target.append(targets[app_name])
                    logger.info(str(evaluation_config['application_name']) + ' target loaded')
                else:
                    logger.info('securechat target loaded')
                    target_obj = targets['securechat']
                    target_obj['label'] = app_name
                    final_target.append(target_obj)
            logger.info('Proceeding to generate prompts final_target' + str(final_target))
            eval_obj = PAIGEvaluator()
            generated_prompts_config = eval_obj.generate_prompts(application_config=evaluation_config, plugins=categories, targets=final_target)
            update_eval_params['config'] = json.dumps(generated_prompts_config)
            update_eval_params['status'] = 'EVALUATING'
            update_eval_params['update_time'] = current_utc_time()
            await update_table_fields('evaluation', update_eval_params, 'eval_id', eval_id)
            del update_eval_params['config']
            proceed_to_eval = True
            logger.info('Prompts generated')
        except Exception as err:
            logger.error('Error: ' + str(err))
            print(traceback.print_exc())
            update_eval_params['status'] = 'FAILED'

        if proceed_to_eval:
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
                eval_id=eval_id,
                generated_prompts=generated_prompts_config,
                custom_prompts=custom_prompts,
                verbose=False
            )
            logger.info('Evaluation completed')
            try:
                results = report["results"]
                cumulative_result = results['prompts']
                update_eval_params['status'] = 'COMPLETED'
                update_eval_params['report_id'] = report['evalId']
                update_eval_params['update_time'] = current_utc_time()
                update_eval_params['cumulative_result'] = str(cumulative_result)
                # update pass counts
                total_passed = list()
                total_failed = list()
                for metric in cumulative_result:
                    metrics = metric['metrics']
                    total_passed.append(str(metrics['testPassCount']))
                    total_failed.append(str(metrics['testFailCount']))
                update_eval_params['passed'] = ', '.join(total_passed)
                update_eval_params['failed'] = ', '.join(total_failed)
                await update_table_fields('evaluation', update_eval_params, 'eval_id', eval_id)
            except Exception as err:
                logger.error('Error while updating DB: ' + str(err))
            print('report genereted')
            return report

    # Run the async operations in a new event loop
    asyncio.run(async_operations())


def threaded_rerun_evaluation(eval_id, generated_prompts_config, static_prompts):
    async def async_operations():
        eval_obj = PAIGEvaluator()
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
        logger.info('triggered rerun')
        try:
            report = eval_obj.evaluate(
                eval_id=eval_id,
                generated_prompts=generated_prompts_config,
                custom_prompts=custom_prompts,
                verbose=False
            )
        except Exception as err:
            print('evluation error', err)
        logger.info('Evaluation completed')
        try:
            update_eval_params = dict()
            results = report["results"]
            cumulative_result = results['prompts']
            update_eval_params['status'] = 'COMPLETED'
            update_eval_params['report_id'] = report['evalId']
            update_eval_params['update_time'] = current_utc_time()
            update_eval_params['cumulative_result'] = str(cumulative_result)
            # update pass counts
            total_passed = list()
            total_failed = list()
            for metric in cumulative_result:
                metrics = metric['metrics']
                total_passed.append(str(metrics['testPassCount']))
                total_failed.append(str(metrics['testFailCount']))
            update_eval_params['passed'] = ', '.join(total_passed)
            update_eval_params['failed'] = ', '.join(total_failed)
            await update_table_fields('evaluation', update_eval_params, 'eval_id', eval_id)
        except Exception as err:
            logger.error('Error while updating DB: ' + str(err))

    # Run the async operations in a new event loop
    asyncio.run(async_operations())


class EvaluationService:

    def __init__(self, evaluation_repository: EvaluationRepository = SingletonDepends(EvaluationRepository)):
        self.evaluation_repository = evaluation_repository

    def get_paig_evaluator(self):
        return PAIGEvaluator()

    async def create_new_evaluation(self, config, owner):
        eval_obj = self.get_paig_evaluator()
        response = config
        initial_config = eval_obj.init()
        response['eval_id'] = initial_config['paig_eval_id']
        try:
            suggested_plugins = eval_obj.get_suggested_plugins(purpose=config['purpose'])
        except Exception as err:
            print('Unhandled error from lib', err)
            suggested_plugins = None
        if isinstance(suggested_plugins, dict):
            response['categories'] = suggested_plugins['plugins']
        else:
            response['categories'] = [
                "pii",
                "excessive-agency",
                "hallucination",
                "hijacking",
                "harmful:cybercrime",
                "pii:api-db",
                "pii:direct",
                "pii:session",
                "pii:social",
                "harmful:privacy"
            ]
        response['owner'] = owner
        model_data = copy.deepcopy(response)
        model_data['categories'] = ', '.join(response['categories'])
        model_data['status'] = 'DRAFTED'
        await self.evaluation_repository.create_new_evaluation(model_data)
        return response

    @Transactional(propagation=Propagation.REQUIRED)
    async def run_evaluation(self, evaluation_config, categories, static_prompts):
        eval_id = evaluation_config['eval_id']
        eval_model = await self.evaluation_repository.get_evaluations_by_field('eval_id', eval_id)
        update_eval_params = {
            "status": "GENERATING",
            "custom_prompts": json.dumps(static_prompts),
            "update_time": current_utc_time(),
            "categories": ', '.join(categories)
        }
        updated_model = await self.evaluation_repository.update_evaluation(update_eval_params, eval_model)
        asyncio.create_task(
            asyncio.to_thread(
                threaded_run_evaluation,
                evaluation_config,
                categories,
                static_prompts
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

    async def get_eval_results_with_filters(self, *args):
        return await self.evaluation_repository.get_eval_results_with_filters(*args)

    async def rerun_evaluation_by_id(self, eval_id, owner):
        try:
            existing_evaluation = await self.evaluation_repository.get_evaluations_by_field('id', eval_id)
            eval_obj = self.get_paig_evaluator()
            new_id = eval_obj.init()
            new_id = new_id['paig_eval_id']
            update_params = {
                'eval_id': new_id,
                'passed': 0,
                'failed': 0,
                'owner': owner,
                'cumulative_result': '',
                'report_id': '',
                'status': 'EVALUATING',
                'config': existing_evaluation.config,
                'application_name': existing_evaluation.application_name,
                'application_client': existing_evaluation.application_client,
                'categories': existing_evaluation.categories,
                'custom_prompts': json.dumps(existing_evaluation.custom_prompts),
                'purpose': existing_evaluation.purpose
            }
            generated_config = existing_evaluation.config
            static_prompts = existing_evaluation.custom_prompts
            static_prompts = json.loads(existing_evaluation.custom_prompts)
            new_model = await self.evaluation_repository.create_new_evaluation(update_params)
        except Exception as err:
            print('exception', err)
            print(traceback.format_exc())
        asyncio.create_task(
            asyncio.to_thread(
                threaded_rerun_evaluation,
                new_id,
                json.loads(generated_config),
                static_prompts
            )
        )
        return new_model
