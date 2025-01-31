from core.utils import SingletonDepends
from api.evaluation.services.eval_config_service import EvaluationConfigService
from api.evaluation.api_schemas.eval_config_schema import EvalConfigFilter
from typing import List
from core.controllers.paginated_response import Pageable


class EvaluationConfigController:

    def __init__(self,
                 eval_config_service: EvaluationConfigService = SingletonDepends(EvaluationConfigService)):
        self.eval_config_service = eval_config_service

    async def get_all_eval_config(self, search_filters: EvalConfigFilter, page_number: int, size: int,
                                   sort: List[str]) -> Pageable:
        """
        Get all evaluation configurations.
        Args:
            search_filters (EvalConfigFilter): The search filters.
            page_number (int): The page number.
            size (int): The number of items per page.
            sort (List[str]): The sort options.
        """
        return await self.eval_config_service.get_all_eval_config(
            search_filters=search_filters,
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