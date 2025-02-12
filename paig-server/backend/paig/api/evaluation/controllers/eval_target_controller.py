from core.utils import SingletonDepends
from api.evaluation.services.eval_target_service import EvaluationTargetService
from api.governance.api_schemas.ai_app import AIApplicationFilter
from typing import List


class EvaluationTargetController:

    def __init__(self,
                 eval_target_service: EvaluationTargetService = SingletonDepends(EvaluationTargetService)):
        self.eval_target_service = eval_target_service

    async def get_all_ai_app_with_host(self, include_query, exclude_query, page_number: int, size: int,
                                   sort: List[str]):
        """
                List AI applications based on the provided filter, pagination, and sorting parameters.

                Args:
                    include_query (AIApplicationFilter): The filter parameters to include.
                    exclude_query (AIApplicationFilter): The filter parameters to exclude.
                    page_number (int): The page number to retrieve.
                    size (int): The number of records to retrieve per page.
                    sort (List[str]): The sorting parameters to apply.

                Returns:
                    Pageable: The paginated response containing the list of AI applications.
                """
        return await self.eval_target_service.get_all_ai_app_with_host(
            include_query,
            exclude_query,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create_app_target(self, body_params: dict):
        """
        Create a new evaluation target for the specified AI application.

        Args:
            body_params (dict): The evaluation target configuration parameters.

        Returns:
            dict: The response message.
        """
        return await self.eval_target_service.create_app_target(body_params=body_params)


    async def update_app_target(self, app_id: int, body_params: dict):
        """
        Update the evaluation target for the specified AI application.

        Args:
            app_id (int): The ID of the AI application.
            body_params (dict): The evaluation target configuration parameters.

        Returns:
            dict: The response message.
        """
        return await self.eval_target_service.update_app_target(target_id=app_id, body_params=body_params)

    async  def delete_app_target(self, app_id: int):
        """
        Delete the evaluation target with the specified ID.

        Args:
            app_id (int): The ID of the evaluation target.

        Returns:
            dict: The response message.
        """
        return await self.eval_target_service.delete_target(app_id=app_id)

    async def get_app_target_by_id(self, app_id: int):
        """
        Retrieve the evaluation target with the specified ID.

        Args:
            app_id (int): The ID of the evaluation target.

        Returns:
            dict: The response message.
        """
        return await self.eval_target_service.get_app_target_by_id(app_id=app_id)