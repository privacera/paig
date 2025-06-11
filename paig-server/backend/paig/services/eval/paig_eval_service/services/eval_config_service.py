import json
import traceback

from ..database.db_operations.eval_target_repository import EvaluationTargetRepository
from core.db_session.transactional import Transactional, Propagation
from core.utils import SingletonDepends, current_utc_time
from ..database.db_operations.eval_config_repository import EvaluationConfigRepository, EvaluationConfigHistoryRepository
import logging
from core.exceptions import NotFoundException, InternalServerError, BadRequestException
from core.controllers.paginated_response import Pageable
from paig_evaluation.paig_evaluator import get_all_plugins

logger = logging.getLogger(__name__)



class EvaluationConfigService:

    def __init__(self,
        eval_config_repository: EvaluationConfigRepository = SingletonDepends(EvaluationConfigRepository),
        eval_config_history_repository: EvaluationConfigHistoryRepository = SingletonDepends(EvaluationConfigHistoryRepository),
        eval_target_repository: EvaluationTargetRepository = SingletonDepends(EvaluationTargetRepository),
    ):
        self.eval_config_repository = eval_config_repository
        self.eval_config_history_repository = eval_config_history_repository
        self.eval_target_repository = eval_target_repository
        # Initialize category name to type mapping from plugins
        all_categories = get_all_plugins()
        plugin_list = all_categories.get("result", [])
        self.category_name_to_type_map = {plugin["Name"]: plugin["Type"] for plugin in plugin_list}

    async def get_all_eval_config(self, search_filters, page_number, size, sort) -> Pageable:
        try:
            return await self.eval_config_repository.get_all_eval_config(search_filters, page_number, size, sort)
        except Exception as e:
            logger.error(f"Error getting evaluation configurations: {e}")
            raise InternalServerError("Error getting evaluation configurations")

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_eval_config(self, body_params: dict):
        app_ids = [int(app_id) for app_id in body_params.get('application_ids', '').split(',') if app_id.strip()]
        apps = await self.eval_target_repository.get_applications_by_in_list('id', app_ids)
        if (len(apps) != len(app_ids)) or len(app_ids) == 0:
            raise BadRequestException("Application names not found")
        try:
            app_names = []
            for app in apps:
                app_names.append(app.name)
            categories = body_params.get('categories', [])
            category_objects = []
            for category in categories:
                category_type = self.category_name_to_type_map.get(category)
                if category_type is None:
                    category_type = "Custom"
                category_objects.append({
                    "name": category,
                    "type": category_type
                })
            body_params['categories'] = json.dumps(category_objects)
            body_params['custom_prompts'] = json.dumps(body_params.get('custom_prompts', []))
            body_params['version'] = 1
            body_params['application_names'] = ','.join(app_names)
            eval_config = await self.eval_config_repository.create_eval_config(body_params)
            body_params['eval_config_id'] = eval_config.id
            config_history =  await self.eval_config_history_repository.create_eval_config_history(body_params)
            return eval_config
        except Exception as e:
            logger.error(f"Error creating evaluation configuration: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Error creating evaluation configuration")

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_eval_config(self, config_id: int, body_params: dict):
        eval_config_model = await self.eval_config_repository.get_eval_config_by_id(config_id)
        if eval_config_model is None:
            raise NotFoundException("Evaluation configuration not found")
        try:
            if 'application_ids' in body_params:
                app_ids = [int(app_id) for app_id in body_params.get('application_ids', '').split(',') if
                           app_id.strip()]
                apps = await self.eval_target_repository.get_applications_by_in_list('id', app_ids)
                if (len(apps) != len(app_ids)) or len(app_ids) == 0:
                    raise BadRequestException("Application names not found")
                app_names = []
                for app in apps:
                    app_names.append(app.name)
                body_params['application_names'] = ','.join(app_names)
            if 'categories' in body_params:
                categories = body_params['categories']
                category_objects = []
                for category in categories:
                    category_type = self.category_name_to_type_map.get(category)
                    if category_type is None:
                        category_type = "Custom"
                    category_objects.append({
                        "name": category,
                        "type": category_type
                    })
                body_params['categories'] = json.dumps(category_objects)
            if 'custom_prompts' in body_params:
                body_params['custom_prompts'] = json.dumps(body_params['custom_prompts'])
            body_params['version'] = eval_config_model.version + 1
            body_params['update_time']: current_utc_time()
            eval_updated_model = await self.eval_config_repository.update_eval_config(body_params, eval_config_model)
            body_params['eval_config_id'] = eval_config_model.id
            eval_config_history_model = await self.eval_config_history_repository.get_eval_config_by_config_id(config_id)
            if eval_config_history_model is None:
                raise NotFoundException("Evaluation configuration history not found")
            await self.eval_config_history_repository.update_eval_config_history(body_params, eval_config_history_model)
            return eval_updated_model
        except Exception as e:
            logger.error(f"Error updating evaluation configuration: {e}")
            raise InternalServerError("Error updating evaluation configuration")

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_eval_config(self, config_id: int):
        eval_config_model = await self.eval_config_repository.get_eval_config_by_id(config_id)
        if eval_config_model is None:
            raise NotFoundException("Evaluation configuration not found")
        try:
            is_deleted = await self.eval_config_repository.delete_eval_config(eval_config_model)
            if is_deleted:
                return {'message': 'Evaluation configuration deleted successfully'}
        except Exception as e:
            logger.error(f"Error deleting evaluation configuration: {e}")
            raise InternalServerError("Error deleting evaluation configuration")
    
    async def get_categories(self, config_id: int):
        eval_config_model = await self.eval_config_repository.get_eval_config_by_id(config_id)
        if eval_config_model is None:
            raise NotFoundException("Evaluation configuration not found")
        categories = json.loads(eval_config_model.categories)
        result = {}
        for category in categories:
            if category["type"] not in result:
                result[category["type"]] = []
            result[category["type"]].append(category["name"])
        return result
        
