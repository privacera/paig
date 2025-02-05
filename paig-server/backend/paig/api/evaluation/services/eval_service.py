import asyncio
import json
import traceback

from api.evaluation.database.db_operations.eval_config_repository import EvaluationConfigHistoryRepository
from api.evaluation.database.db_operations.eval_target_repository import EvaluationTargetRepository
from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from core.utils import SingletonDepends
from api.evaluation.database.db_operations.eval_repository import EvaluationRepository
from core.config import load_config_file
from paig_evaluation.paig_evaluator import PAIGEvaluator
import logging
from core.utils import current_utc_time, format_to_root_path
from core.exceptions import BadRequestException
from tests.insert_access_audits_test_data import app_names

logger = logging.getLogger(__name__)
config = load_config_file()


from core.db_session.transactional import Transactional, Propagation
from core.db_session.standalone_session import update_table_fields

targets = {}

def threaded_run_evaluation(eval_id, eval_config, target_hosts, application_names):
    async def async_operations():
        # Update config in database
        update_eval_params = dict()
        static_prompts = eval_config.custom_prompts
        categories = eval_config.categories
        # Create application configuration
        application_config = {
            "paig_eval_id": eval_id,
            "application_name": ','.join(application_names),
            "purpose": eval_config.purpose,
        }
        eval_obj = PAIGEvaluator()
        if not eval_config.generated_config:
            try:
                generated_prompts_config = eval_obj.generate_prompts(application_config=application_config, plugins=categories, targets=target_hosts)
                eval_config_params = {
                    'generated_config': json.dumps(generated_prompts_config)
                }
                await update_table_fields('eval_config_history', eval_config_params, 'eval_config_id', eval_config.id)
                logger.info('Prompts generated')
            except Exception as err:
                logger.error('Error: ' + str(err))
                print(traceback.print_exc())
                update_eval_params['status'] = 'FAILED'
                return await update_table_fields('evaluation', update_eval_params, 'eval_id', eval_id)
        else:
            generated_prompts_config = eval_config.generated_config
            logger.info('Prompts already generated')

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
        print('report generated')
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

    def __init__(
        self,
        evaluation_repository: EvaluationRepository = SingletonDepends(EvaluationRepository),
        eval_config_history_repository: EvaluationConfigHistoryRepository = SingletonDepends(EvaluationConfigHistoryRepository),
        eval_target_repository: EvaluationTargetRepository = SingletonDepends(EvaluationTargetRepository),
        ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository)
    ):
        self.evaluation_repository = evaluation_repository
        self.eval_config_history_repository = eval_config_history_repository
        self.eval_target_repository = eval_target_repository
        self.ai_app_repository = ai_app_repository

    def get_paig_evaluator(self):
        return PAIGEvaluator()

    async def get_target_hosts(self, apps):
        fina_target = list()
        app_names = list()
        for app in apps:
            target_host = await self.eval_target_repository.get_target_by_app_id(app.id)
            target_host = json.loads(target_host.config)
            target_host['label'] = app.name
            app_names.append(app.name)
            fina_target.append(target_host)
        return fina_target, app_names

    @Transactional(propagation=Propagation.REQUIRED)
    async def run_evaluation(self, eval_config_id, owner):
        eval_config = await self.eval_config_history_repository.get_eval_config_by_config_id(eval_config_id)
        if eval_config is None:
            raise BadRequestException('Invalid evaluation config ID')
        app_ids = [int(app_id) for app_id in eval_config.get('application_ids', '').split(',') if app_id.strip()]
        apps = await self.ai_app_repository.get_ai_application_names_by_in_list('id', app_ids)
        if len(apps) != len(app_ids):
            raise BadRequestException('Application names not found')
        target_hosts, application_names = await self.eval_target_repository.get_target_by_app_id(apps)
        # Insert evaluation record
        eval_id = '123'
        eval_params = {
            "status": "GENERATING",
            "config_id": eval_config_id,
            "owner": owner,
            "eval_id": eval_id
        }
        eval_model= await self.evaluation_repository.create_new_evaluation(eval_params)
        asyncio.create_task(
            asyncio.to_thread(
                threaded_run_evaluation,
                eval_id,
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

    async def get_eval_results_with_filters(self, *args):
        return await self.evaluation_repository.get_eval_results_with_filters(*args)

    async def rerun_evaluation_by_id(self, eval_id, owner):
        try:
            existing_evaluation = await self.evaluation_repository.get_evaluations_by_field('eval_id', eval_id)
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
