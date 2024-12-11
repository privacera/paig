from typing import List, Any, Dict

from api.guardrails.api_schemas.gr_connection import GRConnectionView, GRConnectionFilter
from api.guardrails.services.gr_connections_service import GRConnectionService
from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from core.utils import SingletonDepends


class GRConnectionController:
    """
    Controller class specifically for handling Guardrail connection entities.

    Args:
        gr_connection_service (GRConnectionService): The service class for handling Guardrail connection entities.
    """

    def __init__(self, gr_connection_service: GRConnectionService = SingletonDepends(GRConnectionService)):
        self.gr_connection_service = gr_connection_service

    async def list(self, filter: GRConnectionFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        List Guardrail connections based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (GRConnectionFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of Guardrail connections.
        """
        return await self.gr_connection_service.list(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def list_connection_provider_names(self) -> List[str]:
        """
        List all Guardrail connection provider names.

        Returns:
            List[str]: The list of Guardrail connection provider names.
        """
        return await self.gr_connection_service.list_connection_provider_names()

    @Transactional(propagation=Propagation.REQUIRED)
    async def create(self, request: GRConnectionView) -> GRConnectionView:
        """
        Create a new Guardrail connection.

        Args:
            request (GRConnectionView): The view object representing the Guardrail connection to create.

        Returns:
            GRConnectionView: The created Guardrail connection view object.
        """
        return await self.gr_connection_service.create(request)

    async def get_by_id(self, id: int) -> GRConnectionView:
        """
        Retrieve a Guardrail connection by its ID.

        Args:
            id (int): The ID of the Guardrail connection to retrieve.

        Returns:
            GRConnectionView: The Guardrail connection view object corresponding to the ID.
        """
        return await self.gr_connection_service.get_by_id(id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update(self, id: int, request: GRConnectionView) -> GRConnectionView:
        """
        Update a Guardrail connection identified by its ID.

        Args:
            id (int): The ID of the Guardrail connection to update.
            request (GRConnectionView): The updated view object representing the Guardrail connection.

        Returns:
            GRConnectionView: The updated Guardrail connection view object.
        """
        return await self.gr_connection_service.update(id, request)
        # TODO: background_capture_event(event=UpdateAIApplicationEvent())

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete(self, id: int):
        """
        Delete a Guardrail connection by its ID.

        Args:
            id (int): The ID of the Guardrail connection to delete.
        """
        await self.gr_connection_service.delete(id)
        # TODO: background_capture_event(event=DeleteAIApplicationEvent())

    async def test_connection(self, request: GRConnectionView) -> Dict[str, Any]:
        """
        Test a Guardrail connection.

        Args:
            request (GRConnectionView): The view object representing the Guardrail connection to test.

        Returns:
            Dict[str, Any]: The test connection result.
        """
        return await self.gr_connection_service.test_connection(request)
