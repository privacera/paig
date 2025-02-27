import json
import traceback

from api.evaluation.services.eval_config_service import EvaluationConfigService
from api.evaluation.services.eval_result_service import EvaluationResultService
from api.evaluation.services.eval_service import EvaluationService
from core.utils import SingletonDepends
from core.exceptions import NotFoundException, BadRequestException
from core.controllers.paginated_response import create_pageable_response
from api.evaluation.api_schemas.eval_schema import BaseEvaluationView
from server import logger


class EvaluationController:

    def __init__(self,
                 evaluation_result_service: EvaluationResultService = SingletonDepends(EvaluationResultService),
                 evaluation_service: EvaluationService = SingletonDepends(EvaluationService),
                 evaluation_config_service: EvaluationConfigService = SingletonDepends(EvaluationConfigService)
    ):
        self.evaluation_service = evaluation_service
        self.evaluation_config_service = evaluation_config_service
        self.evaluation_result_service = evaluation_result_service

    async def create_and_run_evaluation(self, eval_params, user):
        try:
            eval_params['owner'] = user
            report_name = eval_params['report_name']
            del eval_params['report_name']
            create_config = await self.evaluation_config_service.create_eval_config(eval_params)
            resp = await self.run_evaluation(create_config.id, user, report_name)
            return resp
        except Exception as e:
            raise BadRequestException(str(e))

    async def run_evaluation(self, eval_config_id, user, report_name):
        try:
            resp = await self.evaluation_service.run_evaluation(eval_config_id, user, base_run_id=None, report_name=report_name)
            return resp
        except Exception as e:
            logger.error(f"Error while running evaluation: {str(e)}")
            raise BadRequestException(str(e))

    async def get_evaluation_results(self, include_filters, exclude_filters, page, size, sort, min_time, max_time):
        if include_filters.owner:
            include_filters.owner = include_filters.owner.strip("*")
        if exclude_filters.owner:
            exclude_filters.owner = exclude_filters.owner.strip("*")
        eval_results, total_count = await self.evaluation_result_service.get_eval_results_with_filters(include_filters, exclude_filters, page, size, sort, min_time, max_time)
        if eval_results is None:
            raise NotFoundException("No results found")
        eval_results_list = [BaseEvaluationView.model_validate(eval_result) for eval_result in eval_results]
        return create_pageable_response(eval_results_list, total_count, page, size, sort)


    async def rerun_evaluation(self, eval_id, user, report_name):
        return await self.evaluation_service.rerun_evaluation_by_id(eval_id, user['username'], report_name)


    async def delete_evaluation(self, eval_id):
        return await self.evaluation_service.delete_evaluation(eval_id)

    async def get_categories(self, purpose):
        return await self.evaluation_service.get_categories(purpose)

    async def get_cumulative_results(self, eval_id):
        return await self.evaluation_result_service.get_cumulative_results_by_uuid(eval_id)

    async def get_detailed_results(self,
        eval_uuid,
        include_query,
        exclude_query,
        page,
        size,
        sort,
        from_time,
        to_time
    ):
        results, total_count =  await self.evaluation_result_service.get_detailed_results_by_uuid(
            eval_uuid,
            include_query,
            exclude_query,
            page,
            size,
            sort,
            from_time,
            to_time
        )
        results_list = []
        for record in results:
            dict_record = dict()
            responses = list()
            dict_record['eval_id'] = record.eval_id
            dict_record['create_time'] = record.create_time
            dict_record['prompt_uuid'] = record.prompt_uuid
            dict_record['prompt'] = record.prompt
            dict_record['id'] = record.id
            for resp in record.responses:
                resp_dict = dict()
                resp_dict['response'] = resp.response
                resp_dict['application_name'] = resp.application_name
                resp_dict['failure_reason'] = resp.failure_reason
                resp_dict['category_score'] = json.loads(resp.category_score)
                resp_dict['status'] = resp.status
                resp_dict['category'] = resp.category
                responses.append(resp_dict)
            dict_record['responses'] = responses
            results_list.append(dict_record)
        return create_pageable_response(results_list, total_count, page, size, sort)


