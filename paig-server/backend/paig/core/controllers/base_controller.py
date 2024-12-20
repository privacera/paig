from typing import TypeVar, Generic, List, Type

from sqlalchemy.exc import NoResultFound

from core.db_session import Base
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.factory.database_initiator import BaseOperations, BaseAPIFilter
from core.controllers.paginated_response import Pageable, create_pageable_response

ModelType = TypeVar("ModelType", bound=Base)
ViewType = TypeVar("ViewType", bound=Base)


class BaseController(Generic[ModelType, ViewType]):
    """
    Generic controller class for handling CRUD operations on models and views.

    Args:
        repository (BaseOperations[ModelType]): The repository handling database operations.
        model_type (Type[ModelType]): The type of the model used in this controller.
        view_type (Type[ViewType]): The type of the view used in this controller.
    """
    def __init__(self, repository: BaseOperations[ModelType], model_type: Type[ModelType], view_type: Type[ViewType]):
        self.repository = repository
        self.model_type = model_type
        self.view_type = view_type

    def get_repository(self) -> BaseOperations[ModelType]:
        """
        Get the repository instance.

        Returns:
            BaseOperations[ModelType]: The repository instance.
        """
        return self.repository

    async def list_records(self, filter: BaseAPIFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of records.

        Args:
            filter (BaseAPIFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing view objects and metadata.
        """
        records, total_count = await self.repository.list_records(filter=filter, page_number=page_number, size=size,
                                                                  sort=sort)
        v_records = [self.view_type.model_validate(record) for record in records]
        return create_pageable_response(v_records, total_count, page_number, size, sort)

    async def create_record(self, v_request: ViewType, exclude_fields: set[str] = None) -> ViewType:
        """
        Create a new record.

        Args:
            v_request (ViewType): The view object representing the record to create.
            exclude_fields (set[str]): The fields to exclude from the creation.

        Returns:
            ViewType: The created view object.
        """
        if exclude_fields is None:
            exclude_fields = set()
        exclude_fields.update({"id", "create_time", "update_time"})
        updated_request = v_request.model_dump(exclude_unset=True, exclude=exclude_fields)
        model = self.model_type(**updated_request)
        return await self.repository.create_record(model)

    async def get_record_by_id(self, id: int) -> ViewType:
        """
        Retrieve a record by its ID.

        Args:
            id (int): The ID of the record to retrieve.

        Returns:
            ViewType: The view object corresponding to the record.
        """
        try:
            return await self.repository.get_record_by_id(id)
        except NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Resource", "id", [id]))

    async def update_record(self, id: int, v_request: ViewType, exclude_fields: set[str] = None) -> ViewType:
        """
        Update a record identified by its ID.

        Args:
            id (int): The ID of the record to update.
            v_request (ViewType): The updated view object.
            exclude_fields (set[str]): The fields to exclude from the update.

        Returns:
            ViewType: The updated view object.
        """
        model = await self.get_record_by_id(id)
        if model is not None:
            if exclude_fields is None:
                exclude_fields = set()
            exclude_fields.update({"create_time", "update_time"})
            updated_data = v_request.model_dump(exclude_unset=True, exclude=exclude_fields)
            model.set_attribute(updated_data)
            return await self.repository.update_record(model)

    async def delete_record(self, id: int):
        """
        Delete a record by its ID.

        Args:
            id (int): The ID of the record to delete.
        """
        model = await self.get_record_by_id(id)
        if model is not None:
            await self.repository.delete_record(model)