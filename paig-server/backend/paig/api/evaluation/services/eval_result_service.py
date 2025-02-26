import json

from core.exceptions import BadRequestException
import logging
from api.evaluation.database.db_operations.eval_repository import EvaluationRepository, EvaluationPromptRepository
from core.utils import SingletonDepends

logger = logging.getLogger(__name__)




class EvaluationResultService:

    def __init__(
        self,
        evaluation_repository: EvaluationRepository = SingletonDepends(EvaluationRepository),
        evaluation_prompt_repository: EvaluationPromptRepository = SingletonDepends(EvaluationPromptRepository)
    ):
        self.evaluation_repository = evaluation_repository
        self.evaluation_prompt_repository = evaluation_prompt_repository

    async def get_eval_results_with_filters(self, *args):
        return await self.evaluation_repository.get_eval_results_with_filters(*args)

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
        return resp_dict

    async def get_detailed_results_by_uuid(self,
        *args
    ):
        return await self.evaluation_prompt_repository.get_detailed_results_by_uuid(*args)
