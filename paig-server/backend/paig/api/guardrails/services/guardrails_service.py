from typing import List

import sqlalchemy

from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GuardrailConfigView
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRConfigModel, GRApplicationModel, \
    GRProviderResponseModel
from api.guardrails.database.db_operations.guardrail_repository import GRApplicationRepository, \
    GRConfigRepository, GRProviderResponseRepository, GuardrailRepository, GuardrailViewRepository
from core.config import load_config_file
from core.controllers.base_controller import BaseController
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
                 gr_app_repository: GRApplicationRepository = SingletonDepends(GRApplicationRepository),
                 gr_config_repository: GRConfigRepository = SingletonDepends(GRConfigRepository),
                 gr_provider_response_repository: GRProviderResponseRepository = SingletonDepends(GRProviderResponseRepository)):
        self.guardrail_repository = guardrail_repository
        self.gr_app_repository = gr_app_repository
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

    def validate_read_request(self, id: int):
        """
        Validate a read request for a Guardrail.

        Args:
            id (int): The ID of the Guardrail to retrieve.
        """
        validate_id(id, "Guardrail ID")

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

        guardrail = await self.get_guardrail_by_name(request.name)
        if guardrail is not None and guardrail.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Guardrail", "name",
                                                        [request.name]))

        guardrail_by_id = None
        try:
            guardrail_by_id = await self.guardrail_repository.get_record_by_id(id)
        except sqlalchemy.exc.NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Resource", "id", [id]))

        if guardrail_by_id is not None and guardrail_by_id.application_key != request.application_key:
            raise BadRequestException(get_error_message(ERROR_FIELD_CANNOT_BE_UPDATED, "Guardrail", "applicationKey"))


    def validate_delete_request(self, id: int):
        """
        Validate a delete request for a Guardrail.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        validate_id(id, "Guardrail ID")

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

    def validate_application_key(self, application_key: str):
        """
        Validate the application key of a Guardrail.

        Args:
            application_key (str): The application key of the Guardrail.
        """
        validate_string_data(application_key, "AI Application key")

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

    # async def validate_ai_application_vector_db_exists_by_name(self, name: List[str]):
    #     """
    #     Validate if the vector DBs exist by their names.
    #
    #     Args:
    #         name (List[str]): The names of the vector DBs.
    #
    #     Raises:
    #         BadRequestException: If any of the vector DBs do not exist.
    #     """
    #     vector_db_names = ",".join(name)
    #     vector_db_filter = VectorDBFilter()
    #     vector_db_filter.name = vector_db_names
    #     vector_db_filter.exact_match = True
    #     records, total_count = await self.vector_db_repository.list_records(filter=vector_db_filter)
    #     if len(name) != total_count:
    #         vector_db_names_from_db = [record.name for record in records]
    #         invalid_vector_db_names = list(set(name) - set(vector_db_names_from_db))
    #         raise BadRequestException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Vector DB", "names",
    #                                                     invalid_vector_db_names))


def create_model_from_dict(model_class, data, exclude_fields=None):
    """
    Create a model instance from a dictionary.

    Args:
        model_class (Base): The model class to create an instance of.
        data (dict): The dictionary containing the data to populate the model.
        exclude_fields (set): The fields to exclude from the model.
    """
    exclude_fields = exclude_fields or set()  # Use provided fields to exclude, or none
    # Get the valid columns for the model
    model_columns = model_class.__table__.columns.keys()

    # Filter out the excluded fields and any non-model fields
    filtered_data = {key: value for key, value in data.items() if key in model_columns and key not in exclude_fields}

    # Create the model instance
    return model_class(**filtered_data)


class GuardrailService(BaseController[GuardrailModel, GuardrailView]):

    def __init__(self,
                 guardrail_repository: GuardrailRepository = SingletonDepends(GuardrailRepository),
                 gr_app_repository: GRApplicationRepository = SingletonDepends(GRApplicationRepository),
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
        self.gr_app_repository = gr_app_repository
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
        guardrail_model = create_model_from_dict(GuardrailModel, request.dict())
        guardrail = await self.repository.create_record(guardrail_model)

        for gr_config in request.guardrail_configs:
            gr_config.guardrail_id = guardrail.id
            gr_config_model = create_model_from_dict(GRConfigModel, gr_config.dict())
            await self.gr_config_repository.create_record(gr_config_model)

        for app_id in request.application_ids:
            gr_app_model = GRApplicationModel(guardrail_id=guardrail.id, application_id=app_id)
            await self.gr_app_repository.create_record(gr_app_model)

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
        self.guardrail_request_validator.validate_read_request(id)
        guardrails = await self.gr_view_repository.get_all(filters={"guardrail_id": id})
        result = GuardrailView.model_validate(guardrails[0])
        result.guardrail_configs = []
        result.guardrail_provider_response = {}
        result.guardrail_connections = {}
        for guardrail in guardrails:
            gr_config = GuardrailConfigView.model_validate(guardrail)
            gr_config.id = guardrail.config_id
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
        return await self.update_record(id, request)

    async def delete(self, id: int):
        """
        Delete a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        self.guardrail_request_validator.validate_delete_request(id)
        await self.delete_record(id)
