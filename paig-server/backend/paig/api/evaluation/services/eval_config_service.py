import json
import traceback

from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from core.db_session.transactional import Transactional, Propagation
from core.utils import SingletonDepends, current_utc_time
from api.evaluation.database.db_operations.eval_config_repository import EvaluationConfigRepository, EvaluationConfigHistoryRepository
import logging
from core.exceptions import NotFoundException, InternalServerError, BadRequestException
from core.controllers.paginated_response import create_pageable_response
from core.controllers.paginated_response import Pageable

logger = logging.getLogger(__name__)



class EvaluationConfigService:

    def __init__(self,
        eval_config_repository: EvaluationConfigRepository = SingletonDepends(EvaluationConfigRepository),
        eval_config_history_repository: EvaluationConfigHistoryRepository = SingletonDepends(EvaluationConfigHistoryRepository),
        ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository),
    ):
        self.eval_config_repository = eval_config_repository
        self.eval_config_history_repository = eval_config_history_repository
        self.ai_app_repository = ai_app_repository

    async def get_all_eval_config(self, search_filters, page_number, size, sort) -> Pageable:
        try:
            return await self.eval_config_repository.get_all_eval_config(search_filters, page_number, size, sort)
        except Exception as e:
            logger.error(f"Error getting evaluation configurations: {e}")
            raise InternalServerError("Error getting evaluation configurations")

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_eval_config(self, body_params: dict):
        try:
            app_ids = [int(app_id) for app_id in body_params.get('application_ids', '').split(',') if app_id.strip()]
            apps = await self.ai_app_repository.get_ai_application_names_by_in_list('id', app_ids)
            if len(apps) != len(app_ids):
                raise BadRequestException("Application names not found")
            app_names = []
            for app in apps:
                app_names.append(app.name)
            body_params['version'] = 1
            body_params['application_names'] = ','.join(app_names)
            eval_config = await self.eval_config_repository.create_eval_config(body_params)
            body_params['eval_config_id'] = eval_config.id
            return await self.eval_config_history_repository.create_eval_config_history(body_params)
        except Exception as e:
            logger.error(f"Error creating evaluation configuration: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Error creating evaluation configuration")

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_eval_config(self, config_id: int, body_params: dict):
        try:
            eval_config_model = await self.eval_config_repository.get_eval_config_by_id(config_id)
            if eval_config_model is None:
                raise NotFoundException("Evaluation configuration not found")
            body_params['version'] = eval_config_model.version + 1
            body_params['update_time']: current_utc_time()
            eval_updated_model = await self.eval_config_repository.update_eval_config(body_params, eval_config_model)
            body_params['eval_config_id'] = eval_config_model.id
            return await self.eval_config_history_repository.create_eval_config_history(body_params)
        except Exception as e:
            logger.error(f"Error updating evaluation configuration: {e}")
            raise InternalServerError("Error updating evaluation configuration")

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_eval_config(self, config_id: int):
        try:
            eval_config_model = await self.eval_config_repository.get_eval_config_by_id(config_id)
            if eval_config_model is None:
                raise NotFoundException("Evaluation configuration not found")
            is_deleted = await self.eval_config_repository.delete_eval_config(eval_config_model)
            if is_deleted:
                return {'message': 'Evaluation configuration deleted successfully'}
        except Exception as e:
            logger.error(f"Error deleting evaluation configuration: {e}")
            raise InternalServerError("Error deleting evaluation configuration")

