import json
import traceback
from core.utils import SingletonDepends
from api.evaluation.database.db_operations.eval_target_repository import EvaluationTargetRepository
import logging
from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from core.exceptions import NotFoundException, InternalServerError, BadRequestException
from core.controllers.paginated_response import create_pageable_response


logger = logging.getLogger(__name__)


def transform_eval_target(app_name, eval_target):
    eval_target_dict = dict()
    eval_target_dict['id'] = eval_target['url']
    eval_target_dict['label'] = app_name
    eval_config = dict()
    eval_config['method'] = eval_target['method']
    if isinstance(eval_target['headers'], dict):
        eval_config['headers'] = eval_target['headers']
    else:
        try:
            eval_target['headers'] = json.loads(eval_target['headers'])
        except Exception as e:
            raise BadRequestException("Invalid headers format")
    if isinstance(eval_target['body'], dict):
        eval_config['body'] = eval_target['body']
    else:
        try:
            eval_target['body'] = json.loads(eval_target['body'])
        except Exception as e:
            raise BadRequestException("Invalid body format")
    eval_config['transformResponse'] = eval_target['transformResponse']
    eval_target_dict['config'] = eval_target
    return json.dumps(eval_target_dict)

class EvaluationTargetService:

    def __init__(self,
        eval_target_repository: EvaluationTargetRepository = SingletonDepends(EvaluationTargetRepository),
        ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository)
    ):
        self.eval_target_repository = eval_target_repository
        self.ai_app_repository = ai_app_repository


    async def get_all_ai_app_with_host(self, search_filters, page_number, size, sort):
        try:
            ai_apps, total_count = await self.ai_app_repository.get_ai_application_with_host(search_filters, page_number, size, sort)
            if ai_apps is None:
                raise NotFoundException("No applications found")
            ai_app_list = list()
            for ai_app in ai_apps:
                hosted = False
                if ai_app.host and len(ai_app.host) > 0:
                    hosted = True
                ai_app_dict = dict()
                ai_app_dict['id'] = ai_app.id
                ai_app_dict['name'] = ai_app.name
                ai_app_dict['status'] = ai_app.status
                ai_app_dict['hosted'] = hosted
                ai_app_list.append(ai_app_dict)
            return create_pageable_response(ai_app_list, total_count, page_number, size, sort)
        except Exception as e:
            logger.error(f"Error in get_all_ai_app_with_host: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    async def create_app_target(self, app_id, body_params):
        ai_app = await self.ai_app_repository.get_record_by_id(app_id)
        if ai_app is None:
            raise NotFoundException(f"No AI application found with id {app_id}")
        transformed_eval = transform_eval_target(ai_app.name, body_params)
        try:
            eval_target = await self.eval_target_repository.create_app_target(app_id, transformed_eval)
            return eval_target
        except Exception as e:
            logger.error(f"Error in create_app_target: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    async def update_app_target(self, app_id, body_params):
        ai_app = await self.ai_app_repository.get_record_by_id(app_id)
        if ai_app is None:
            raise NotFoundException(f"No AI application found with id {app_id}")
        transformed_eval = transform_eval_target(ai_app.name, body_params)
        try:
            target_model = await self.eval_target_repository.get_target_by_app_id(app_id)
            if target_model is None:
                raise NotFoundException(f"No AI application found with id {app_id}")
            eval_target = await self.eval_target_repository.update_app_target(transformed_eval, target_model)
            return eval_target
        except Exception as e:
            logger.error(f"Error in update_app_target: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")

    async def delete_target(self, app_id):
        try:
            target_model = await self.eval_target_repository.get_target_by_app_id(app_id)
            if target_model is None:
                raise NotFoundException(f"No AI application found with id {app_id}")
            eval_target = await self.eval_target_repository.delete_target(target_model)
            return eval_target
        except Exception as e:
            logger.error(f"Error in delete_target: {e}")
            logger.error(traceback.format_exc())
            raise InternalServerError("Internal server error")