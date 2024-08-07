from typing import List

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import (get_error_message, ERROR_RESOURCE_ALREADY_EXISTS,
                                                   ERROR_ALLOWED_VALUES)
from core.utils import validate_id, validate_string_data, SingletonDepends
from api.governance.api_schemas.metadata_key import MetadataKeyView, MetadataKeyFilter
from api.governance.database.db_models.metadata_key_model import VectorDBMetaDataKeyModel, MetadataType, ValueDataType
from api.governance.database.db_operations.metadata_key_repository import MetadataKeyRepository


class MetadataKeyRequestValidator:
    """
    Validator class for validating Metadata requests.

    Args:
        metadata_key_repository (MetadataKeyRepository): The repository handling Metadata database operations.
    """

    def __init__(self, metadata_key_repository: MetadataKeyRepository = SingletonDepends(MetadataKeyRepository)):
        self.metadata_key_repository = metadata_key_repository

    async def validate_create_request(self, request: MetadataKeyView):
        """
        Validate a create request for Metadata.

        Args:
            request (MetadataKeyView): The view object representing the Metadata to create.
        """
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_type(request.type)
        self.validate_data_type(request.data_type)
        await self.validate_metadata_exists_by_name(request.name)


    def validate_read_request(self, id: int):
        """
        Validate a read request for a Metadata Key.

        Args:
            id (int): The ID of the Metadata Key to retrieve.
        """
        validate_id(id, "Metadata Key ID")

    async def validate_update_request(self, id: int, request: MetadataKeyView):
        """
        Validate an update request for an Metadata Key.

        Args:
            id (int): The ID of the Metadata Key to update.
            request (MetadataKeyView): The updated view object representing the Metadata Key.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        validate_id(id, "Metadata Key ID")
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_type(request.type)
        self.validate_data_type(request.data_type)

        meta_data = await self.get_metadata_by_name(request.name)
        if meta_data is not None and meta_data.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Metadata Key", "name",
                                                        [request.name]))


    def validate_delete_request(self, id: int):
        """
        Validate a delete request for an Metadata Key.

        Args:
            id (int): The ID of the Metadata Key to delete.
        """
        validate_id(id, "Metadata Key ID")

    def validate_name(self, name: str):
        """
        Validate the name of Metadata Key value.

        Args:
            name (str): The name of the Metadata Key.
        """
        validate_string_data(name, "Metadata Key name")

    def validate_description(self, description: str):
        """
        Validate the description of the Metadata Key.

        Args:
            description (str): The description of the Metadata Key.
        """
        validate_string_data(description, "Metadata Key description", required=False, max_length=4000)

    def validate_type(self, type: str):
        """
        Validate the type of Metadata Key.

        Args:
            type (str): The type of the Metadata Key.
        """
        if type != MetadataType.USER_DEFINED.value:
            raise BadRequestException(get_error_message(ERROR_ALLOWED_VALUES, "Metadata Key Type", [type], [MetadataType.USER_DEFINED.value]))

    def validate_data_type(self, data_type: str):
        """
        Validate the name of Metadata Key data_type.

        Args:
            data_type (str): The data_type of the Metadata Key.
        """
        if data_type != ValueDataType.MULTI_VALUE.value:
            raise BadRequestException(get_error_message(ERROR_ALLOWED_VALUES, "Metadata Key Data Type", [data_type], [ValueDataType.MULTI_VALUE.value]))

    async def validate_metadata_exists_by_name(self, name: str):
        """
        Check if a Metadata already exists by its name.

        Args:
            name (str): The name of the Metadata.

        Raises:
            BadRequestException: If the Metadata with the same name already exists.
        """
        metadata = await self.get_metadata_by_name(name)
        if metadata is not None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Metadata Key", "name", name))

    async def get_metadata_by_name(self, name: str):
        """
        Retrieve Metadata Key by its name.

        Args:
            name (str): The name of the Metadata Key.

        Returns:
            VectorDBMetaDataKeyModel: The Metadata Key model corresponding to the name.
        """
        meta_data_filter = MetadataKeyFilter()
        meta_data_filter.name = name
        meta_data_filter.exact_match = True
        records, total_count = await self.metadata_key_repository.list_records(filter=meta_data_filter)
        if total_count > 0:
            return records[0]
        return None


class MetadataKeyService(BaseController[VectorDBMetaDataKeyModel, MetadataKeyView]):

    def __init__(self, metadata_repository: MetadataKeyRepository = SingletonDepends(MetadataKeyRepository),
                 metadata_request_validator: MetadataKeyRequestValidator = SingletonDepends(MetadataKeyRequestValidator)):
        """
        Initialize the Metadata KeyService.

        Args:
            metadata_repository (MetadataKeyRepository): The repository handling Metadata Key database operations.
        """
        super().__init__(
            metadata_repository,
            VectorDBMetaDataKeyModel,
            MetadataKeyView
        )
        self.metadata_request_validator = metadata_request_validator

    def get_repository(self) -> MetadataKeyRepository:
        """
        Get the Metadata Key repository.

        Returns:
            MetadataKeyRepository: The Metadata Key repository.
        """
        return self.repository

    async def list_metadata(self, filter: MetadataKeyFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of Metadata Key.

        Args:
            filter (MetadataKeyFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Metadata Key view objects and other fields.
        """
        return await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def list_metadata_by_ids(self, ids: List[int]) -> List[MetadataKeyView]:
        """
        Retrieve a list of Metadata Key by their IDs.

        Args:
            ids (List[int]): The list of Metadata Key IDs to retrieve.

        Returns:
            List[MetadataKeyView]: A list of Metadata Key view objects.
        """
        return await self.repository.get_all({"id": ids}, apply_in_list_filter=True)

    async def create_metadata(self, request: MetadataKeyView) -> MetadataKeyView:
        """
        Create a new Metadata Key.

        Args:
            request (MetadataKeyView): The view object representing the Metadata Key to create.

        Returns:
            MetadataKeyView: The created Metadata Key view object.
        """
        await self.metadata_request_validator.validate_create_request(request)
        return await self.create_record(request)

    async def get_metadata_by_id(self, id: int) -> MetadataKeyView:
        """
        Retrieve an Metadata Key by its ID.

        Args:
            id (int): The ID of the Metadata Key to retrieve.

        Returns:
            MetadataKeyView: The Metadata Key view object corresponding to the ID.
        """
        self.metadata_request_validator.validate_read_request(id)
        return await self.get_record_by_id(id)

    async def update_metadata(self, id: int, request: MetadataKeyView) -> MetadataKeyView:
        """
        Update Metadata Key identified by its ID.

        Args:
            id (int): The ID of the Metadata Key to update.
            request (MetadataKeyView): The updated view object representing the Metadata Key.

        Returns:
            MetadataKeyView: The updated Metadata Key view object.
        """
        await self.metadata_request_validator.validate_update_request(id, request)
        return await self.update_record(id, request)

    async def delete_metadata(self, id: int):
        """
        Delete Metadata Key by its ID.

        Args:
            id (int): The ID of the Metadata Key to delete.
        """
        self.metadata_request_validator.validate_delete_request(id)
        await self.delete_record(id)