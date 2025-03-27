import json

from core.exceptions import BadRequestException
import logging
from api.evaluation.database.db_operations.eval_repository import EvaluationRepository, EvaluationPromptRepository, EvaluationResponseRepository
from core.utils import SingletonDepends

logger = logging.getLogger(__name__)




class EvaluationResultService:

    def __init__(
        self,
        evaluation_repository: EvaluationRepository = SingletonDepends(EvaluationRepository),
        evaluation_prompt_repository: EvaluationPromptRepository = SingletonDepends(EvaluationPromptRepository),
        evaluation_response_repository: EvaluationResponseRepository = SingletonDepends(EvaluationResponseRepository)
    ):
        self.evaluation_repository = evaluation_repository
        self.evaluation_prompt_repository = evaluation_prompt_repository
        self.evaluation_response_repository = evaluation_response_repository

    async def get_eval_results_with_filters(self, *args):
        return await self.evaluation_repository.get_eval_results_with_filters(*args)

    async def get_evaluation(self, uuid):
        return await self.evaluation_repository.get_evaluations_by_field('eval_id', uuid)

    async def get_cumulative_results_by_uuid(self, uuid):
        model = await self.evaluation_repository.get_evaluations_by_field("eval_id", uuid)
        if model is None:
            raise BadRequestException(f"No results found for {uuid}")
        cumulative_result = model.cumulative_result
        if cumulative_result is None:
            raise BadRequestException(f"No results found for {uuid}")
        cumulative_result = json.loads(cumulative_result)
        resp_list = list()
        resp_dict = {}
        for result in cumulative_result:
            resp = dict()
            resp['application_name'] = result['provider']
            resp['passed'] = result['metrics']['testPassCount']
            resp['failed'] = result['metrics']['testFailCount']
            resp['error'] = result['metrics']['testErrorCount']
            resp['categories'] = result['metrics']['namedScores']
            resp['total_categories'] = result['metrics']['namedScoresCount']
            resp_list.append(resp)
        resp_dict['result'] = resp_list
        resp_dict['eval_id'] = model.eval_id
        resp_dict['report_name'] = model.name
        resp_dict['owner'] = model.owner
        resp_dict['create_time'] = model.create_time
        resp_dict["target_users"] = model.target_users
        return resp_dict

    async def get_detailed_results_by_uuid(self,
        *args
    ):
        return await self.evaluation_prompt_repository.get_detailed_results_by_uuid(*args)

    async def get_result_by_severity(self, uuid):
        rows = await self.evaluation_response_repository.get_result_by_severity(uuid)
        # Initialize all possible severity levels with 0
        severity_levels = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "CRITICAL": 0}
        result_dict = dict()
        # Update with actual values from the query result
        for severity, app_name, count in rows:
            severity_level = severity_levels
            if severity in severity_levels:
                severity_level[severity] = count
            result_dict[app_name] = severity_level
        return result_dict

    async def get_result_by_category(self, uuid):
        return await self.evaluation_response_repository.get_result_by_category(uuid)

    async def get_all_categories_from_result(self, uuid):
        return await self.evaluation_response_repository.get_all_categories_from_result(uuid)