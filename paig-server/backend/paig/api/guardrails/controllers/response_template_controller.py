from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.guardrails.api_schemas.response_template import ResponseTemplateView, ResponseTemplateFilter
from api.guardrails.services.response_template_service import ResponseTemplateService
from core.utils import SingletonDepends


class ResponseTemplateController:
    """
    Controller class specifically for handling ResponseTemplate entities.

    Args:
        response_template_service (ResponseTemplateService): The service class for handling ResponseTemplate entities.
    """

    def __init__(self,
                 response_template_service: ResponseTemplateService = SingletonDepends(ResponseTemplateService)):
        self.response_template_service = response_template_service

    async def list_response_templates(self, filter: ResponseTemplateFilter, page_number: int, size: int,
                        sort: List[str]) -> Pageable:
        """
        List ResponseTemplate based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (ResponseTemplateFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of ResponseTemplate.
        """
        return await self.response_template_service.list_response_templates(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_response_template(self, request: ResponseTemplateView) -> ResponseTemplateView:
        """
        Create a new ResponseTemplate.

        Args:
            request (ResponseTemplateView): The view object representing the ResponseTemplate to create.

        Returns:
            ResponseTemplateView: The created ResponseTemplate view object.
        """
        return await self.response_template_service.create_response_template(request)

    async def get_response_template_by_id(self, id: int) -> ResponseTemplateView:
        """
        Retrieve an ResponseTemplate by its ID.

        Args:
            id (int): The ID of the ResponseTemplate to retrieve.

        Returns:
            ResponseTemplateView: The ResponseTemplate view object corresponding to the ID.
        """
        return await self.response_template_service.get_response_template_by_id(id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_response_template(self, id: int, request: ResponseTemplateView) -> ResponseTemplateView:
        """
        Update an ResponseTemplate identified by its ID.

        Args:
            id (int): The ID of the ResponseTemplate to update.
            request (ResponseTemplateView): The updated view object representing the ResponseTemplate.

        Returns:
            ResponseTemplateView: The updated ResponseTemplate view object.
        """
        return await self.response_template_service.update_response_template(id, request)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_response_template(self, id: int):
        """
        Delete an ResponseTemplate by its ID.

        Args:
            id (int): The ID of the ResponseTemplate to delete.
        """
        response_template = await self.get_response_template_by_id(id)
        await self.response_template_service.delete_response_template(id)
