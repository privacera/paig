from core.utils import SingletonDepends
from api.evaluation.services.eval_config_service import EvaluationConfigService
from api.evaluation.api_schemas.eval_config_schema import EvalConfigFilter
from typing import List
from core.controllers.paginated_response import Pageable
from api.evaluation.api_schemas.eval_config_schema import include_query_params, exclude_query_params

class EvaluationConfigController:

    def __init__(self,
                 eval_config_service: EvaluationConfigService = SingletonDepends(EvaluationConfigService)):
        self.eval_config_service = eval_config_service

    async def get_all_eval_config(self, includeQuery:include_query_params, excludeQuery: exclude_query_params, page_number: int, size: int,
                                   sort: List[str]) -> Pageable:
        """
        Get all evaluation configurations.
        Args:
            includeQuery (EvalConfigFilter): The filter for the evaluation configuration.
            excludeQuery (EvalConfigFilter): The filter for the evaluation configuration.
            page_number (int): The page number.
            size (int): The number of items per page.
            sort (List[str]): The sort options.
        """

        if excludeQuery:
            exclude_list = []
            for key, value in excludeQuery.model_dump().items():
                if value:
                    exclude_list.append(key)
                    if hasattr(includeQuery, key):
                        setattr(includeQuery, key, value)
            if len(exclude_list) > 0:
                includeQuery.exclude_match = True
                includeQuery.exclude_list = ','.join(exclude_list)
        return await self.eval_config_service.get_all_eval_config(
            search_filters=includeQuery,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create_eval_config(self, body_params: dict):
        """
        Create a new evaluation target for the specified AI application.

        Args:
            app_id (int): The ID of the AI application.
            body_params (dict): The evaluation target configuration parameters.

        Returns:
            dict: The response message.
        """
        return await self.eval_config_service.create_eval_config(body_params=body_params)


    async def update_eval_config(self, config_id: int, body_params: dict):
        """
        Update an existing evaluation target for the specified AI application.

        Args:
            config_id (int): The ID of the evaluation target.
            body_params (dict): The evaluation target configuration parameters.

        Returns:
            dict: The response message.
        """
        return await self.eval_config_service.update_eval_config(config_id=config_id, body_params=body_params)

    async def delete_eval_config(self, config_id: int):
        """
        Delete an existing evaluation target for the specified AI application.

        Args:
            config_id (int): The ID of the evaluation target.

        Returns:
            dict: The response message.
        """
        return await self.eval_config_service.delete_eval_config(config_id=config_id)