from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_IN_USE
from api.governance.api_schemas.vector_db import VectorDBView, VectorDBFilter
from api.governance.services.ai_app_service import AIAppService
from api.governance.services.vector_db_service import VectorDBService
from core.utils import SingletonDepends
from core.middlewares.usage import background_capture_event
from core.factory.events import CreateVectorDBEvent, UpdateVectorDBEvent, DeleteVectorDBEvent


class VectorDBController:
    """
    Controller class specifically for handling Vector DB entities.

    Args:
        vector_db_service (VectorDBService): The service handling Vector DB operations.
        ai_app_service (AIAppService): The service handling AI application operations.
    """

    def __init__(self,
                 vector_db_service: VectorDBService = SingletonDepends(VectorDBService),
                 ai_app_service: AIAppService = SingletonDepends(AIAppService)):
        self.vector_db_service = vector_db_service
        self.ai_app_service = ai_app_service

    async def list_vector_dbs(self, vector_db_filter: VectorDBFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of Vector DBs.

        Args:
            vector_db_filter (VectorDBFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Vector DB view objects and metadata.
        """
        return await self.vector_db_service.list_vector_dbs(vector_db_filter, page_number, size, sort)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_vector_db(self, request: VectorDBView) -> VectorDBView:
        """
        Create a new Vector DB.

        Args:
            request (VectorDBView): The view object representing the Vector DB to create.

        Returns:
            VectorDBView: The created Vector DB view object.
        """
        created_vector_db = await self.vector_db_service.create_vector_db(request)
        await background_capture_event(event=CreateVectorDBEvent(vector_db_type=created_vector_db.type.value))
        return created_vector_db

    async def get_vector_db_by_id(self, id: int) -> VectorDBView:
        """
        Retrieve a Vector DB by its ID.

        Args:
            id (int): The ID of the Vector DB to retrieve.

        Returns:
            VectorDBView: The Vector DB view object corresponding to the ID.
        """
        result = await self.vector_db_service.get_vector_db_by_id(id)
        ai_applications = await self.ai_app_service.list_ai_applications_by_vector_db(result.name)
        result.ai_applications = [ai_app.name for ai_app in ai_applications]
        return result

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_vector_db(self, id: int):
        """
        Delete a Vector DB by its ID.

        Args:
            id (int): The ID of the Vector DB to delete.
        """
        result = await self.vector_db_service.get_vector_db_by_id(id)
        ai_applications = await self.ai_app_service.list_ai_applications_by_vector_db(result.name)
        if ai_applications:
            ai_application_names = [ai_app.name for ai_app in ai_applications]
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_IN_USE, "Vector DB", "AI Applications", ai_application_names))
        await self.vector_db_service.delete_vector_db(id)
        await background_capture_event(event=DeleteVectorDBEvent(vector_db_type=result.type.value))

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_vector_db(self, id: int, request: VectorDBView) -> VectorDBView:
        """
        Update a Vector DB identified by its ID.

        Args:
            id (int): The ID of the Vector DB to update.
            request (VectorDBView): The updated view object representing the Vector DB.

        Returns:
            VectorDBView: The updated Vector DB view object.
        """
        updated_vector_db = await self.vector_db_service.update_vector_db(id, request)
        await background_capture_event(event=UpdateVectorDBEvent(vector_db_type=updated_vector_db.type.value))
        return updated_vector_db
