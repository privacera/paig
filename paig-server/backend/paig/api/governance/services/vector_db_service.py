from typing import List

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS
from core.utils import validate_string_data, validate_boolean, validate_id, SingletonDepends
from api.governance.api_schemas.ai_app import AIApplicationFilter
from api.governance.api_schemas.vector_db import VectorDBView, VectorDBFilter
from api.governance.database.db_models.vector_db_model import VectorDBModel
from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from api.governance.database.db_operations.vector_db_repository import VectorDBRepository


class VectorDBRequestValidator:
    """
    Validator class for validating Vector DB application requests.

    Args:
        vector_db_repository (VectorDBRepository): The repository handling Vector DB application database operations.
        ai_app_repository (AIAppRepository): The repository handling AI application database operations.
    """

    def __init__(self, vector_db_repository: VectorDBRepository = SingletonDepends(VectorDBRepository), ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository)):
        self.vector_db_repository = vector_db_repository
        self.ai_app_repository = ai_app_repository

    async def validate_create_request(self, request: VectorDBView):
        """
        Validate a create request for an Vector DB.

        Args:
            request (VectorDBView): The view object representing the Vector DB to create.
        """
        self.validate_status(request.status)
        self.validate_user_enforcement(request.user_enforcement)
        self.validate_group_enforcement(request.group_enforcement)
        self.validate_name(request.name)
        self.validate_description(request.description)

        vector_db = await self.get_vector_db_by_name(request.name)
        if vector_db:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Vector DB", "name", [request.name]))

    def validate_read_request(self, id: int):
        """
        Validate a read request for a Vector DB.

        Args:
            id (int): The ID of the Vector DB to retrieve.
        """
        validate_id(id, "Vector DB ID")

    async def validate_update_request(self, id: int, request: VectorDBView):
        """
        Validate an update request for a Vector DB.

        Args:
            id (int): The ID of the Vector DB to update.
            request (VectorDBView): The updated view object representing the Vector DB.
        """
        validate_id(id, "Vector DB ID")
        self.validate_status(request.status)
        self.validate_user_enforcement(request.group_enforcement)
        self.validate_group_enforcement(request.user_enforcement)
        self.validate_name(request.name)
        self.validate_description(request.description)

        vector_db = await self.get_vector_db_by_name(request.name)
        if vector_db and vector_db.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Vector DB", "name", [request.name]))

    def validate_delete_request(self, id: int):
        """
        Validate a delete request for a Vector DB.

        Args:
            id (int): The ID of the Vector DB to delete.
        """
        validate_id(id, "Vector DB ID")


    def validate_user_enforcement(self, user_enforcement: int):
        """
        Validate the user enforcement of a Vector DB.

        Args:
            user_enforcement (int): The user enforcement of the Vector DB.
        """
        validate_boolean(user_enforcement, "Vector DB user enforcement")

    def validate_group_enforcement(self, group_enforcement: int):
        """
        Validate the group enforcement of a Vector DB.

        Args:
            group_enforcement (int): The group enforcement of the Vector DB.
        """
        validate_boolean(group_enforcement, "Vector DB group enforcement")

    def validate_status(self, status: int):
        """
        Validate the status of a Vector DB.

        Args:
            status (int): The status of the Vector DB.
        """
        validate_boolean(status, "Vector DB status")

    def validate_name(self, name: str):
        """
        Validate the name of a Vector DB.

        Args:
            name (str): The name of the Vector DB.
        """
        validate_string_data(name, "Vector DB name")

    def validate_description(self, description: str):
        """
        Validate the description of a Vector DB.

        Args:
            description (str): The description of the Vector DB.
        """
        validate_string_data(description, "Vector DB description", required=False, max_length=4000)

    async def get_vector_db_by_name(self, name:str):
        """
        Retrieve a Vector DB by its name.

        Args:
            name (str): The name of the Vector DB to retrieve.

        Returns:
            VectorDBModel: The Vector DB model corresponding to the name.
        """
        filter = VectorDBFilter()
        filter.name = name
        filter.exact_match = True
        records, total_count = await self.vector_db_repository.list_records(filter=filter)
        if total_count > 0:
            return records[0]
        return None


class VectorDBService(BaseController[VectorDBModel, VectorDBView]):
    """
    Service class specifically for handling Vector DB entities.

    Args:
        vector_db_repository (VectorDBRepository): The repository handling Vector DB database operations.
    """

    def __init__(self,
                 vector_db_repository: VectorDBRepository = SingletonDepends(VectorDBRepository),
                 ai_app_repository: AIAppRepository = SingletonDepends(AIAppRepository),
                 vector_db_request_validator: VectorDBRequestValidator = SingletonDepends(VectorDBRequestValidator)):
        super().__init__(vector_db_repository, VectorDBModel, VectorDBView)
        self.ai_app_repository = ai_app_repository
        self.vector_db_request_validator = vector_db_request_validator

    def get_repository(self) -> VectorDBRepository:
        """
        Get the AI application repository.

        Returns:
            VectorDBRepository: The AI application repository.
        """
        return self.repository

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
        vector_db_map = {}
        vector_db_list = []
        records = await self.list_records(
            filter=vector_db_filter,
            page_number=page_number,
            size=size,
            sort=sort
        )
        vector_dbs = ""
        if records.totalElements > 0:
            for record in records.content:
                vector_db_map[record.name] = record
                vector_db_list.append(record.name)
            vector_dbs = ",".join(vector_db_list)
        ai_app_filter = AIApplicationFilter()
        ai_app_filter.vector_dbs = vector_dbs
        ai_app_filter.exact_match = True
        ai_app_records, ai_app_total_count = await self.ai_app_repository.list_records(filter=ai_app_filter)
        for ai_app in ai_app_records:
            if ai_app.vector_dbs is not None:
                for vector_db in ai_app.vector_dbs:
                    vector_db_map[vector_db].ai_applications.append(ai_app.name)

        return records

    async def create_vector_db(self, request: VectorDBView) -> VectorDBView:
        """
        Create a new Vector DB.

        Args:
            request (VectorDBView): The view object representing the Vector DB to create.

        Returns:
            VectorDBView: The created Vector DB view object.
        """
        await self.vector_db_request_validator.validate_create_request(request)
        # TODO: see if we can have an alternate way of removing field
        delattr(request, "ai_applications")
        return await self.create_record(request)

    async def get_vector_db_by_id(self, id: int) -> VectorDBView:
        """
        Retrieve a Vector DB by its ID.

        Args:
            id (int): The ID of the Vector DB to retrieve.

        Returns:
            VectorDBView: The Vector DB view object corresponding to the ID.
        """
        self.vector_db_request_validator.validate_read_request(id)
        return await self.get_record_by_id(id)

    async def delete_vector_db(self, id: int):
        """
        Delete a Vector DB by its ID.

        Args:
            id (int): The ID of the Vector DB to delete.
        """
        self.vector_db_request_validator.validate_delete_request(id)
        await self.delete_record(id)

    async def update_vector_db(self, id: int, request: VectorDBView) -> VectorDBView:
        """
        Update a Vector DB identified by its ID.

        Args:
            id (int): The ID of the Vector DB to update.
            request (VectorDBView): The updated view object representing the Vector DB.

        Returns:
            VectorDBView: The updated Vector DB view object.
        """
        await self.vector_db_request_validator.validate_update_request(id, request)
        # TODO: see if we can have an alternate way of removing field
        delattr(request, "ai_applications")
        return await self.update_record(id, request)

    async def get_vector_db_by_name(self, name: str) -> VectorDBModel:
        """
        Retrieve a Vector DB by its name.

        Args:
            name (str): The name of the Vector DB to retrieve.

        Returns:
            VectorDBModel: The Vector DB with the specified name.
        """
        repository = self.get_repository()
        return await repository.get_vector_db_by_name(name)