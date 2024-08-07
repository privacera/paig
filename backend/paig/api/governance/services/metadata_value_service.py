from typing import List

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import (get_error_message, ERROR_RESOURCE_ALREADY_EXISTS)
from core.utils import validate_id, validate_string_data, SingletonDepends
from api.governance.api_schemas.metadata_value import MetadataValueView, MetadataValueFilter
from api.governance.database.db_models.metadata_value_model import VectorDBMetaDataValueModel
from api.governance.database.db_operations.metadata_value_repository import MetadataValueRepository


class MetadataValueRequestValidator:
    """
    Validator class for validating Metadata value requests.

    Args:
        metadata_value_repository (MetadataValueRepository): The repository handling Metadata attribute database operations.
    """

    def __init__(self, metadata_value_repository: MetadataValueRepository = SingletonDepends(MetadataValueRepository)):
        self.metadata_value_repository = metadata_value_repository

    async def validate_create_request(self, request: MetadataValueView):
        """
        Validate a create request for Metadata value.

        Args:
            request (MetadataValueView): The view object representing the Metadata attribute to create.
        """
        validate_id(request.metadata_id, "Metadata ID")
        self.validate_metadata_attr_value(request.metadata_value)
        metadata_attr = await self.get_metadata_attr_by_values(request)
        if metadata_attr is not None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Metadata Attribute", "value",
                                                        [request.metadata_value]))

    def validate_read_request(self, id: int):
        """
        Validate a read request for an Metadata Value.

        Args:
            id (int): The ID of the Metadata Val to retrieve.
        """
        validate_id(id, "Metadata attribute value ID")

    async def validate_update_request(self, id: int, request: MetadataValueView):
        """
        Validate an update request for an Metadata Value.

        Args:
            id (int): The ID of the Metadata Val to update.
            request (MetadataValueView): The updated view object representing the Metadata Val.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        validate_id(id, "Metadata attribute value ID")
        validate_id(request.metadata_id, "Metadata ID")
        self.validate_name(request.metadata_name)
        self.validate_metadata_attr_value(request.metadata_value)
        meta_data_attr = await self.get_metadata_attr_by_values(request)
        if meta_data_attr is not None and meta_data_attr.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Metadata Attribute", "value",
                                                        [request.metadata_value]))

    def validate_delete_request(self, id: int):
        """
        Validate a delete request for an Metadata Value.

        Args:
            id (int): The ID of the Metadata Value to delete.
        """
        validate_id(id, "Metadata attribute value ID")

    def validate_name(self, name: str):
        """
        Validate the name of Metadata Value.

        Args:
            name (str): The name of the Metadata Value.
        """
        validate_string_data(name, "Metadata name")

    def validate_metadata_attr_value(self, value: str):
        """
        Validate the value of the Metadata Value.

        Args:
            value (str): The value of the Metadata Value.
        """
        validate_string_data(value, "Metadata attribute value", required=False, max_length=4000)

    async def get_metadata_attr_by_values(self, metadata_attr: MetadataValueView):
        """
        Retrieve an Metadata Value by its name.

        Args:
            metadata_attr: The Metadata Value view object.
        """
        meta_data_filter = MetadataValueFilter()
        meta_data_filter.metadata_value = metadata_attr.metadata_value
        meta_data_filter.exact_match = True
        records, total_count = await self.metadata_value_repository.list_records(filter=meta_data_filter)
        if total_count > 0:
            return records[0]
        return None


class MetadataValueService(BaseController[VectorDBMetaDataValueModel, MetadataValueView]):

    def __init__(self, metadata_attr_repository: MetadataValueRepository = SingletonDepends(MetadataValueRepository),
                 metadata_attr_request_validator: MetadataValueRequestValidator = SingletonDepends(MetadataValueRequestValidator)):
        """
        Initialize the MetadataAttrService.

        Args:
            metadata_attr_repository (MetadataValueRepository): The repository handling Metadata Value database operations.
        """
        super().__init__(
            metadata_attr_repository,
            VectorDBMetaDataValueModel,
            MetadataValueView
        )
        self.metadata_attr_request_validator = metadata_attr_request_validator

    def get_repository(self) -> MetadataValueRepository:
        """
        Get the Metadata Value repository.

        Returns:
            MetadataValueRepository: The Metadata Value repository.
        """
        return self.repository

    async def list_metadata_values(self, filter: MetadataValueFilter, page_number: int, size: int,
                                   sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of Metadata.

        Args:
            filter (MetadataValueFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Metadata view objects and other fields.
        """
        return await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create_metadata_values(self, request: MetadataValueView) -> MetadataValueView:
        """
        Create a new Metadata Value.

        Args:
            request (MetadataValueView): The view object representing the Metadata Value to create.

        Returns:
            MetadataValueView: The created Metadata Value view object.
        """
        await self.metadata_attr_request_validator.validate_create_request(request)
        delattr(request, "metadata_name")
        return await self.create_record(request)

    async def get_metadata_value_by_id(self, id: int) -> MetadataValueView:
        """
        Retrieve an Metadata Value by its ID.

        Args:
            id (int): The ID of the Metadata Value to retrieve.

        Returns:
            MetadataValueView: The Metadata Value view object corresponding to the ID.
        """
        self.metadata_attr_request_validator.validate_read_request(id)
        return await self.get_record_by_id(id)

    async def update_metadata_value(self, id: int, request: MetadataValueView) -> MetadataValueView:
        """
        Update Metadata Value identified by its ID.

        Args:
            id (int): The ID of the Metadata Value to update.
            request (MetadataValueView): The updated view object representing the Metadata Value.

        Returns:
            MetadataValueView: The updated Metadata Value view object.
        """
        await self.metadata_attr_request_validator.validate_update_request(id, request)
        delattr(request, "metadata_name")
        return await self.update_record(id, request)

    async def delete_metadata_value(self, id: int):
        """
        Delete Metadata Value by its ID.

        Args:
            id (int): The ID of the Metadata Value to delete.
        """
        self.metadata_attr_request_validator.validate_delete_request(id)
        await self.delete_record(id)
