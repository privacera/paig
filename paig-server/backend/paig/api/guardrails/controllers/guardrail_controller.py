from typing import List

from api.guardrails.api_schemas.guardrail import GuardrailFilter, GuardrailView, GuardrailsDataView
from api.guardrails.services.guardrails_service import GuardrailService
from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from core.utils import SingletonDepends


class GuardrailController:
    """
    Controller class specifically for handling Guardrail entities.

    Args:
        guardrail_service (GuardrailService): The service class for handling Guardrail entities.
    """

    def __init__(self, guardrail_service: GuardrailService = SingletonDepends(GuardrailService)):
        self.guardrail_service = guardrail_service

    async def list(self, filter: GuardrailFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        List Guardrails based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (GuardrailFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of Guardrails.
        """
        return await self.guardrail_service.list(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def create(self, request: GuardrailView) -> GuardrailView:
        """
        Create a new Guardrail.

        Args:
            request (GuardrailView): The view object representing the Guardrail to create.

        Returns:
            GuardrailView: The created Guardrail view object.
        """
        return await self.guardrail_service.create(request)

    async def get_by_id(self, id: int, extended: bool) -> GuardrailView:
        """
        Retrieve a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to retrieve.
            extended (bool): Include extended information

        Returns:
            GuardrailView: The Guardrail view object corresponding to the ID.
        """
        return await self.guardrail_service.get_by_id(id, extended)

    async def get_all_by_app_key(self, app_key: str, last_known_version: int = None) -> GuardrailsDataView:
        """
        Retrieve all Guardrails by the application key.

        Args:
            app_key (str): The application key to search for.
            last_known_version (int): The last known version to compare against.

        Returns:
            GuardrailsDataView: The view object containing the app_key, version and list of Guardrails.
        """
        return await self.guardrail_service.get_all_by_app_key(app_key, last_known_version)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update(self, id: int, request: GuardrailView) -> GuardrailView:
        """
        Update a Guardrail identified by its ID.

        Args:
            id (int): The ID of the Guardrail to update.
            request (GuardrailView): The updated view object representing the Guardrail.

        Returns:
            GuardrailView: The updated Guardrail view object.
        """
        return await self.guardrail_service.update(id, request)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete(self, id: int):
        """
        Delete a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        await self.guardrail_service.delete(id)
