from typing import List

import sqlalchemy

from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GuardrailConfigView
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRConfigModel, \
    GRProviderResponseModel
from api.guardrails.database.db_operations.guardrail_repository import \
    GRConfigRepository, GRProviderResponseRepository, GuardrailRepository, GuardrailViewRepository
from core.config import load_config_file
from core.controllers.base_controller import BaseController, ViewType, ModelType
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException, NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS, \
    ERROR_RESOURCE_NOT_FOUND, ERROR_FIELD_CANNOT_BE_UPDATED
from core.utils import validate_id, validate_string_data, validate_boolean, SingletonDepends

config = load_config_file()


class GuardrailRequestValidator:
    """
    Validator class for validating Guardrail requests.

    Args:
        guardrail_repository (GuardrailRepository): The repository handling Guardrail database operations.
    """

    def __init__(self,
                 guardrail_repository: GuardrailRepository = SingletonDepends(GuardrailRepository),
                 gr_config_repository: GRConfigRepository = SingletonDepends(GRConfigRepository),
                 gr_provider_response_repository: GRProviderResponseRepository = SingletonDepends(GRProviderResponseRepository)):
        self.guardrail_repository = guardrail_repository
        self.gr_config_repository = gr_config_repository
        self.gr_provider_response_repository = gr_provider_response_repository

    async def validate_create_request(self, request: GuardrailView):
        """
        Validate a create request for a Guardrail.

        Args:
            request (GuardrailView): The view object representing the Guardrail to create.
        """
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        await self.validate_guardrail_exists_by_name(request.name)

    def validate_status(self, status: int):
        """
        Validate the status of a Guardrail.

        Args:
            status (int): The status of the Guardrail.
        """
        validate_boolean(status, "Guardrail status")

    async def validate_read_request(self, id: int):
        """
        Validate a read request for a Guardrail.

        Args:
            id (int): The ID of the Guardrail to retrieve.
        """
        validate_id(id, "Guardrail ID")
        await self.validate_guardrail_exists_by_id(id)

    async def validate_update_request(self, id: int, request: GuardrailView):
        """
        Validate an update request for a Guardrail.

        Args:
            id (int): The ID of the Guardrail to update.
            request (GuardrailView): The updated view object representing the Guardrail.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        validate_id(id, "Guardrail ID")
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        await self.validate_guardrail_exists_by_id(id)

        guardrail = await self.get_guardrail_by_name(request.name)
        if guardrail is not None and guardrail.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Guardrail", "name",
                                                        [request.name]))

    async def validate_guardrail_exists_by_id(self, id):
        try:
            await self.guardrail_repository.get_record_by_id(id)
        except sqlalchemy.exc.NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Guardrail", "id", [id]))

    async def validate_delete_request(self, id: int):
        """
        Validate a delete request for a Guardrail.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        validate_id(id, "Guardrail ID")
        await self.validate_guardrail_exists_by_id(id)

    def validate_name(self, name: str):
        """
        Validate the name of a Guardrail.

        Args:
            name (str): The name of the Guardrail.
        """
        validate_string_data(name, "AI Application name")

    def validate_description(self, description: str):
        """
        Validate the description of a Guardrail.

        Args:
            description (str): The description of the Guardrail.
        """
        validate_string_data(description, "AI Application description", required=False, max_length=4000)

    async def validate_guardrail_exists_by_name(self, name: str):
        """
        Check if a Guardrail already exists by its name.

        Args:
            name (str): The name of the Guardrail.

        Raises:
            BadRequestException: If a Guardrail with the same name already exists.
        """
        guardrail = await self.get_guardrail_by_name(name)
        if guardrail is not None:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Guardrail", "name", [name]))

    async def get_guardrail_by_name(self, name: str):
        """
        Retrieve a Guardrail by its name.

        Args:
            name (str): The name of the Guardrail.

        Returns:
            GuardrailModel: The Guardrail model corresponding to the name.
        """
        filter = GuardrailFilter()
        filter.name = name
        filter.exact_match = True
        records, total_count = await self.guardrail_repository.list_records(filter=filter)
        if total_count > 0:
            return records[0]
        return None

def transform_view_to_model(model_type: ModelType, view_data: ViewType, exclude_fields: set[str]=None):
    """
    Create a model instance from a dictionary.

    Args:
        model_type (Base): The model class to create an instance of.
        view_data (dict): The dictionary containing the view data to populate the model.
        exclude_fields (set): The fields to exclude from the model.
    """
    exclude_fields = exclude_fields or set()  # Use provided fields to exclude, or none
    # Get the valid columns for the model
    model_columns = model_type.__table__.columns.keys()

    # Filter out the excluded fields and any non-model fields
    filtered_data = {key: value for key, value in view_data.dict().items() if key in model_columns and key not in exclude_fields}

    # Create the model instance
    return model_type(**filtered_data)


class GuardrailService(BaseController[GuardrailModel, GuardrailView]):

    def __init__(self,
                 guardrail_repository: GuardrailRepository = SingletonDepends(GuardrailRepository),
                 gr_config_repository: GRConfigRepository = SingletonDepends(GRConfigRepository),
                 gr_provider_response_repository: GRProviderResponseRepository = SingletonDepends(GRProviderResponseRepository),
                 gr_view_repository: GuardrailViewRepository = SingletonDepends(GuardrailViewRepository),
                 guardrail_request_validator: GuardrailRequestValidator = SingletonDepends(GuardrailRequestValidator)):
        """
        Initialize the GuardrailService.

        Args:
            guardrail_repository (GuardrailRepository): The repository handling Guardrail database operations.
        """
        super().__init__(
            guardrail_repository,
            GuardrailModel,
            GuardrailView
        )
        self.guardrail_request_validator = guardrail_request_validator
        self.gr_config_repository = gr_config_repository
        self.gr_provider_response_repository = gr_provider_response_repository
        self.gr_view_repository = gr_view_repository

    def get_repository(self) -> GuardrailRepository:
        """
        Get the Guardrail repository.

        Returns:
            GuardrailRepository: The Guardrail repository.
        """
        return self.repository

    async def list(self, filter: GuardrailFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Retrieve a paginated list of Guardrails.

        Args:
            filter (GuardrailFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing Guardrail view objects and metadata.
        """
        return await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    async def create(self, request: GuardrailView) -> GuardrailView:
        """
        Create a new Guardrail.

        Args:
            request (GuardrailView): The view object representing the Guardrail to create.

        Returns:
            GuardrailView: The created Guardrail view object.
        """
        await self.guardrail_request_validator.validate_create_request(request)
        guardrail_model = transform_view_to_model(GuardrailModel, request)
        guardrail = await self.repository.create_record(guardrail_model)

        for gr_config in request.guardrail_configs:
            gr_config.guardrail_id = guardrail.id
            gr_config_model = transform_view_to_model(GRConfigModel, gr_config)
            await self.gr_config_repository.create_record(gr_config_model)

        # TODO: replace below dummy response with actual by creating guardrails to end service
        guardrail_provider_response: dict = {
            "AWS": {
               "createdAt": "2024-10-16T07:14:06.102135",
               "guardrailArn": "test_arn",
               "guardrailId": "test_id",
               "version": "1"
            },
            "Azure": {
                "createdAt": "2024-10-16T07:14:06.102135",
                "guardrailArn": "test_arn"
            }
        }

        for provider, response in guardrail_provider_response.items():
            gr_resp_model = GRProviderResponseModel(guardrail_id=guardrail.id, guardrail_provider=provider, response_data=response)
            await self.gr_provider_response_repository.create_record(gr_resp_model)

        result = GuardrailView(**request.dict())
        result.id = guardrail.id
        result.status = guardrail.status
        result.create_time = guardrail.create_time
        result.update_time = guardrail.update_time
        result.guardrail_provider_response = guardrail_provider_response

        return result

    async def get_by_id(self, id: int) -> GuardrailView:
        """
        Retrieve a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to retrieve.

        Returns:
            GuardrailView: The Guardrail view object corresponding to the ID.
        """
        await self.guardrail_request_validator.validate_read_request(id)
        guardrails = await self.gr_view_repository.get_all(filters={"guardrail_id": id})
        result = GuardrailView.model_validate(guardrails[0])
        result.id = guardrails[0].guardrail_id
        result.guardrail_configs = []
        result.guardrail_provider_response = {}
        result.guardrail_connections = {}
        for guardrail in guardrails:
            gr_config = GuardrailConfigView.model_validate(guardrail)
            result.guardrail_configs.append(gr_config)
            result.guardrail_provider_response[guardrail.guardrail_provider] = guardrail.guardrail_provider_response
            result.guardrail_connections[guardrail.guardrail_provider] = guardrail.guardrail_connection

        return result

    async def update(self, id: int, request: GuardrailView) -> GuardrailView:
        """
        Update a Guardrail identified by its ID.

        Args:
            id (int): The ID of the Guardrail to update.
            request (GuardrailView): The updated view object representing the Guardrail.

        Returns:
            GuardrailView: The updated Guardrail view object.
        """
        await self.guardrail_request_validator.validate_update_request(id, request)
        guardrail_model = await self.repository.get_record_by_id(id)
        updated_guardrail = GuardrailView()
        if guardrail_model is not None:
            updated_guardrail = transform_view_to_model(GuardrailModel, request, exclude_fields={"create_time", "update_time", "version"})
            guardrail_model.set_attribute(updated_guardrail)
            guardrail_model.version = guardrail_model.version + 1
            updated_guardrail = await self.repository.update_record(guardrail_model)

        updated_guardrail.guardrail_configs = []
        for req_gr_config in request.guardrail_configs:
            gr_config_model = await self.gr_config_repository.get_record_by_id(req_gr_config.id)
            updated_gr_config_model = transform_view_to_model(GRConfigModel, req_gr_config, exclude_fields={"create_time", "update_time"})
            gr_config_model.set_attribute(updated_gr_config_model)
            updated_gr_config = await self.gr_config_repository.update_record(gr_config_model)
            updated_guardrail.guardrail_configs.append(updated_gr_config)

        return updated_guardrail

    async def delete(self, id: int):
        """
        Delete a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        await self.guardrail_request_validator.validate_delete_request(id)
        await self.delete_record(id)
