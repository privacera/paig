from typing import List

from api.guardrails import GuardrailProvider
from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import (get_error_message, ERROR_RESOURCE_ALREADY_EXISTS,
                                                   ERROR_ALLOWED_VALUES)
from core.utils import validate_id, validate_string_data, SingletonDepends
from api.guardrails.api_schemas.gr_sensitive_data import GRSensitiveDataView, GRSensitiveDataFilter
from api.guardrails.database.db_models.gr_sensitive_data_model import GRSensitiveDataModel
from api.guardrails.database.db_operations.gr_sensitive_data_repository import GRSensitiveDataRepository


class GRSensitiveDataRequestValidator:
    """
    Validator class for validating Guardrail Sensitive Data requests.

    Args:
        gr_sensitive_data_repository (GRSensitiveDataRepository): The repository handling Guardrail Sensitive Data database operations.
    """

    def __init__(self, gr_sensitive_data_repository: GRSensitiveDataRepository = SingletonDepends(GRSensitiveDataRepository)):
        self.gr_sensitive_data_repository = gr_sensitive_data_repository

    async def validate_create_request(self, request: GRSensitiveDataView):
        """
        Validate a create request for GRSensitiveData.

        Args:
            request (GRSensitiveDataView): The view object representing the Guardrail Sensitive Data to create.
        """
        self.validate_name(request.name)
        await self.validate_gr_sensitive_data_exists_by_name_and_provider(request.name, request.guardrail_provider)

    def validate_read_request(self, id: int):
        """
        Validate a read request for an GRSensitiveData.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to retrieve.
        """
        validate_id(id, "Guardrail Sensitive Data ID")

    async def validate_update_request(self, id: int, request: GRSensitiveDataView):
        """
        Validate an update request for an GRSensitiveData.

        Args:
            id (int): The ID of the GRSensitiveData to update.
            request (GRSensitiveDataView): The updated view object representing the Guardrail Sensitive Data.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        validate_id(id, "Guardrail Sensitive Data ID")
        self.validate_name(request.name)

        gr_sensitive_data = await self.get_gr_sensitive_data_by_name_and_provider(request.name, request.guardrail_provider)
        if gr_sensitive_data is not None and gr_sensitive_data.id != id:
            message = get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Guardrail Sensitive Data ", "name", [request.name])
            message += " and provider ['" + request.guardrail_provider.value + "']"
            raise BadRequestException(message)

    def validate_delete_request(self, id: int):
        """
        Validate a delete request for an GRSensitiveData.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to delete.
        """
        validate_id(id, "Guardrail Sensitive Data ID")

    def validate_name(self, name: str):
        """
        Validate the name of GRSensitiveData value.

        Args:
            name (str): The name of the GRSensitiveData.
        """
        validate_string_data(name, "Guardrail Sensitive Data name")

    async def validate_gr_sensitive_data_exists_by_name_and_provider(self, name: str, provider: GuardrailProvider):
        """
        Check if a GRSensitiveData already exists by its name and provider.

        Args:
            name (str): The name of the Guardrail Sensitive Data.
            provider (GuardrailProvider): The provider of the Guardrail Sensitive Data.

        Raises:
            BadRequestException: If the Guardrail Sensitive Data with the same name and guardrail provider already exists.
        """
        gr_sensitive_data = await self.get_gr_sensitive_data_by_name_and_provider(name, provider)
        if gr_sensitive_data is not None:
            message = get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Guardrail Sensitive Data ", "name", [name])
            message += " and provider ['" + provider.value + "']"
            raise BadRequestException(message)

    async def get_gr_sensitive_data_by_name_and_provider(self, name: str, provider: GuardrailProvider):
        """
        Retrieve GRSensitiveData by its name.

        Args:
            name (str): The name of the Guardrail Sensitive Data.
            provider (GuardrailProvider): The provider of the Guardrail Sensitive Data.

        Returns:
            GRSensitiveDataModel: The GRSensitiveData model corresponding to the name.
        """
        gr_sensitive_data_filter = GRSensitiveDataFilter()
        gr_sensitive_data_filter.name = name
        gr_sensitive_data_filter.guardrail_provider = provider
        gr_sensitive_data_filter.exact_match = True
        records, total_count = await self.gr_sensitive_data_repository.list_records(filter=gr_sensitive_data_filter)
        if total_count > 0:
            return records[0]
        return None


class GRSensitiveDataService(BaseController[GRSensitiveDataModel, GRSensitiveDataView]):

    def __init__(self, gr_sensitive_data_repository: GRSensitiveDataRepository = SingletonDepends(GRSensitiveDataRepository),
                 gr_sensitive_data_request_validator: GRSensitiveDataRequestValidator = SingletonDepends(GRSensitiveDataRequestValidator)):
        """
        Initialize the Guardrail Sensitive Data.

        Args:
            gr_sensitive_data_repository (GRSensitiveDataRepository): The repository handling GRSensitiveData database operations.
        """
        super().__init__(
            gr_sensitive_data_repository,
            GRSensitiveDataModel,
            GRSensitiveDataView
        )
        self.gr_sensitive_data_request_validator = gr_sensitive_data_request_validator

    def get_repository(self) -> GRSensitiveDataRepository:
        """
        Get the Guardrail Sensitive Data repository.

        Returns:
            GRSensitiveDataRepository: The Guardrail Sensitive Data repository.
        """
        return self.repository

    async def list_gr_sensitive_datas(self, filter: GRSensitiveDataFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of GRSensitiveData.

        Args:
            filter (GRSensitiveDataFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Guardrail Sensitive Data view objects and other fields.
        """
        return await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create_gr_sensitive_data(self, request: GRSensitiveDataView) -> GRSensitiveDataView:
        """
        Create a new Guardrail Sensitive Data.

        Args:
            request (GRSensitiveDataView): The view object representing the GRSensitiveData to create.

        Returns:
            GRSensitiveDataView: The created Guardrail Sensitive Data view object.
        """
        await self.gr_sensitive_data_request_validator.validate_create_request(request)
        return await self.create_record(request)

    async def get_gr_sensitive_data_by_id(self, id: int) -> GRSensitiveDataView:
        """
        Retrieve Guardrail Sensitive Data by its ID.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to retrieve.

        Returns:
            GRSensitiveDataView: The Guardrail Sensitive Data view object corresponding to the ID.
        """
        self.gr_sensitive_data_request_validator.validate_read_request(id)
        return await self.get_record_by_id(id)

    async def update_gr_sensitive_data(self, id: int, request: GRSensitiveDataView) -> GRSensitiveDataView:
        """
        Update Guardrail Sensitive Data identified by its ID.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to update.
            request (GRSensitiveDataView): The updated view object representing the Guardrail Sensitive Data.

        Returns:
            GRSensitiveDataView: The updated Guardrail Sensitive Data view object.
        """
        await self.gr_sensitive_data_request_validator.validate_update_request(id, request)
        return await self.update_record(id, request)

    async def delete_gr_sensitive_data(self, id: int):
        """
        Delete Guardrail Sensitive Data by its ID.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to delete.
        """
        self.gr_sensitive_data_request_validator.validate_delete_request(id)
        await self.delete_record(id)