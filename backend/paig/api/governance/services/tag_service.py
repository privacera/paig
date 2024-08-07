from typing import List

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import (get_error_message, ERROR_RESOURCE_ALREADY_EXISTS,
                                                   ERROR_ALLOWED_VALUES)
from core.utils import validate_id, validate_string_data, SingletonDepends
from api.governance.api_schemas.tag import TagView, TagFilter
from api.governance.database.db_models.tag_model import TagType, TagModel
from api.governance.database.db_operations.tag_repository import TagRepository


class TagRequestValidator:
    """
    Validator class for validating Tag requests.

    Args:
        tag_repository (TagRepository): The repository handling Tag database operations.
    """

    def __init__(self, tag_repository: TagRepository = SingletonDepends(TagRepository)):
        self.tag_repository = tag_repository

    async def validate_create_request(self, request: TagView):
        """
        Validate a create request for Tag.

        Args:
            request (TagView): The view object representing the Tag to create.
        """
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_type(request.type)
        await self.validate_tag_exists_by_name(request.name)

    def validate_read_request(self, id: int):
        """
        Validate a read request for an Tag.

        Args:
            id (int): The ID of the Tag to retrieve.
        """
        validate_id(id, "Tag ID")

    async def validate_update_request(self, id: int, request: TagView):
        """
        Validate an update request for an Tag.

        Args:
            id (int): The ID of the Tag to update.
            request (TagView): The updated view object representing the Tag.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        validate_id(id, "Tag ID")
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_type(request.type)

        tag = await self.get_tag_by_name(request.name)
        if tag is not None and tag.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Tag", "name",
                                                        [request.name]))

    def validate_delete_request(self, id: int):
        """
        Validate a delete request for an Tag.

        Args:
            id (int): The ID of the Tag to delete.
        """
        validate_id(id, "Tag ID")

    def validate_name(self, name: str):
        """
        Validate the name of Tag value.

        Args:
            name (str): The name of the Tag.
        """
        validate_string_data(name, "Tag name")

    def validate_description(self, description: str):
        """
        Validate the description of the Tag.

        Args:
            description (str): The description of the Tag.
        """
        validate_string_data(description, "Tag description", required=False, max_length=4000)

    def validate_type(self, type: str):
        """
        Validate the type of Tag.

        Args:
            type (str): The type of the Tag.
        """
        if type != TagType.USER_DEFINED.value:
            raise BadRequestException(get_error_message(ERROR_ALLOWED_VALUES, "Tag Type", [type], [TagType.USER_DEFINED.value]))

    async def validate_tag_exists_by_name(self, name: str):
        """
        Check if a Tag already exists by its name.

        Args:
            name (str): The name of the Tag.

        Raises:
            BadRequestException: If the Tag with the same name already exists.
        """
        tag = await self.get_tag_by_name(name)
        if tag is not None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Tag", "name", [name]))

    async def get_tag_by_name(self, name: str):
        """
        Retrieve Tag by its name.

        Args:
            name (str): The name of the Tag.

        Returns:
            TagModel: The Tag model corresponding to the name.
        """
        tag_filter = TagFilter()
        tag_filter.name = name
        tag_filter.exact_match = True
        records, total_count = await self.tag_repository.list_records(filter=tag_filter)
        if total_count > 0:
            return records[0]
        return None


class TagService(BaseController[TagModel, TagView]):

    def __init__(self, tag_repository: TagRepository = SingletonDepends(TagRepository),
                 tag_request_validator: TagRequestValidator = SingletonDepends(TagRequestValidator)):
        """
        Initialize the TagService.

        Args:
            tag_repository (TagRepository): The repository handling Tag database operations.
        """
        super().__init__(
            tag_repository,
            TagModel,
            TagView
        )
        self.tag_request_validator = tag_request_validator

    def get_repository(self) -> TagRepository:
        """
        Get the Tag repository.

        Returns:
            TagRepository: The Tag repository.
        """
        return self.repository

    async def list_tags(self, filter: TagFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of Tag.

        Args:
            filter (TagFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Tag view objects and other fields.
        """
        return await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create_tag(self, request: TagView) -> TagView:
        """
        Create a new Tag.

        Args:
            request (TagView): The view object representing the Tag to create.

        Returns:
            TagView: The created Tag view object.
        """
        await self.tag_request_validator.validate_create_request(request)
        return await self.create_record(request)

    async def get_tag_by_id(self, id: int) -> TagView:
        """
        Retrieve an Tag by its ID.

        Args:
            id (int): The ID of the Tag to retrieve.

        Returns:
            TagView: The Tag view object corresponding to the ID.
        """
        self.tag_request_validator.validate_read_request(id)
        return await self.get_record_by_id(id)

    async def update_tag(self, id: int, request: TagView) -> TagView:
        """
        Update Tag identified by its ID.

        Args:
            id (int): The ID of the Tag to update.
            request (TagView): The updated view object representing the Tag.

        Returns:
            TagView: The updated Tag view object.
        """
        await self.tag_request_validator.validate_update_request(id, request)
        return await self.update_record(id, request)

    async def delete_tag(self, id: int):
        """
        Delete Tag by its ID.

        Args:
            id (int): The ID of the Tag to delete.
        """
        self.tag_request_validator.validate_delete_request(id)
        await self.delete_record(id)