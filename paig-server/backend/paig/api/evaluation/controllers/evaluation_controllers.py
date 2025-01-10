import traceback

from api.evaluation.services.evaluation_service import EvaluationService
from core.utils import SingletonDepends
from core.exceptions import NotFoundException, BadRequestException
from core.controllers.paginated_response import create_pageable_response
from api.evaluation.api_schemas.evaluation_schema import BaseEvaluationView

class EvaluationController:

    def __init__(self,
                 evaluation_service: EvaluationService = SingletonDepends(EvaluationService)):
        self.evaluation_service = evaluation_service

    async def create_new_evaluation(self, eval_params, user):
        try:
            resp = await self.evaluation_service.create_new_evaluation(eval_params.dict(), user['username'])
            return resp
        except Exception as e:
            return {"error": str(e)}

    async def run_evaluation(self, evaluation_config):
        try:
            evaluation_config = evaluation_config.dict()
            plugins = evaluation_config['categories']
            static_prompts = evaluation_config['static_prompts']
            evaluation_config.pop("static_prompts", None)
            evaluation_config.pop("categories", None)
            resp = await self.evaluation_service.run_evaluation(evaluation_config, plugins, static_prompts)
            return resp
        except Exception as e:
            print(traceback.print_exc())
            return {"error": str(e)}

    async def get_evaluation_results(self, include_filters, exclude_filters, page, size, sort, min_time, max_time):
        if include_filters.owner:
            include_filters.owner = include_filters.owner.strip("*")
        if include_filters.application_name:
            include_filters.application_name = include_filters.application_name.strip("*")
        if exclude_filters.owner:
            exclude_filters.owner = exclude_filters.owner.strip("*")
        if exclude_filters.application_name:
            exclude_filters.application_name = exclude_filters.application_name.strip("*")
        eval_results, total_count = await self.evaluation_service.get_eval_results_with_filters(include_filters, exclude_filters, page, size, sort, min_time, max_time)
        if eval_results is None:
            raise NotFoundException("No results found")
        eval_results_list = [BaseEvaluationView.model_validate(eval_result) for eval_result in eval_results]
        return create_pageable_response(eval_results_list, total_count, page, size, sort)


    async def rerun_evaluation(self, id, user):
        print('here2')
        return await self.evaluation_service.rerun_evaluation_by_id(id, user['username'])


    async def delete_evaluation(self, eval_id):
        print('here2')
        return await self.evaluation_service.delete_evaluation(eval_id)

