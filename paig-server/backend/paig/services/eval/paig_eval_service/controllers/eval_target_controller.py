from core.utils import SingletonDepends
from ..services.eval_target_service import EvaluationTargetService
from typing import List
import httpx
from fastapi import HTTPException


class EvaluationTargetController:

    def __init__(self,
                 eval_target_service: EvaluationTargetService = SingletonDepends(EvaluationTargetService)):
        self.eval_target_service = eval_target_service

    async def get_all_ai_app_with_host(self, include_query, exclude_query, page_number: int, size: int,
                                   sort: List[str]):
        """
                List AI applications based on the provided filter, pagination, and sorting parameters.

                Args:
                    include_query (Filter): The filter parameters to include.
                    exclude_query (Filter): The filter parameters to exclude.
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
    
    async def test_app_target(self, request_data: dict):
        """
        Test the connection to a target AI application by making an HTTP request using the provided details.

        Args:
            request_data (dict): Contains method, url, headers, and body (payload).

        Returns:
            dict: The response status and message or error details.
        """
        method = request_data.get("method", "GET").upper()
        url = str(request_data.get("url")) 
        headers = request_data.get("headers", {})
        payload = request_data.get("body", None)

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                if isinstance(payload, dict):
                    response = await client.request(method, url, headers=headers, json=payload)
                else:
                    response = await client.request(method, url, headers=headers, content=payload)

            return {
                "success": True,
                "status_code": response.status_code,
                "response_body": response.text
            }
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to connect to the target application: {str(e)}"
            )


