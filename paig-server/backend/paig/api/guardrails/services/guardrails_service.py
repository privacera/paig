from typing import List, Dict, Set

import sqlalchemy

from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GRConfigView
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRConfigModel, \
    GRProviderResponseModel, GRApplicationModel
from api.guardrails.database.db_operations.guardrail_repository import \
    GRConfigRepository, GRProviderResponseRepository, GuardrailRepository, GuardrailViewRepository, \
    GRApplicationRepository
from core.config import load_config_file
from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException, NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS, \
    ERROR_RESOURCE_NOT_FOUND
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
                 gr_provider_response_repository: GRProviderResponseRepository = SingletonDepends(
                     GRProviderResponseRepository)):
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


class GuardrailService(BaseController[GuardrailModel, GuardrailView]):

    def __init__(self,
                 guardrail_repository: GuardrailRepository = SingletonDepends(GuardrailRepository),
                    gr_app_repository: GuardrailRepository = SingletonDepends(GRApplicationRepository),
                 gr_config_repository: GRConfigRepository = SingletonDepends(GRConfigRepository),
                 gr_provider_response_repository: GRProviderResponseRepository = SingletonDepends(
                     GRProviderResponseRepository),
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
        # Validate the create request
        await self.guardrail_request_validator.validate_create_request(request)

        # Create the Guardrail
        guardrail_model = GuardrailModel()
        guardrail_model.set_attribute(request.model_dump(exclude={"create_time", "update_time", "version"}))
        guardrail = await self.repository.create_record(guardrail_model)

        # Create Guardrail Applications
        for gr_app_key in request.application_keys:
            gr_app_model = GRApplicationModel()
            gr_app_model.application_key = gr_app_key
            gr_app_model.guardrail_id = guardrail.id
            # set other fields like app name, app id by getting data from gov service
            await self.gr_app_repository.create_record(gr_app_model)

        # Create Guardrail Configs
        for gr_config in request.guardrail_configs:
            gr_config.guardrail_id = guardrail.id
            gr_config_model = GRConfigModel()
            gr_config_model.set_attribute(gr_config.model_dump(exclude={"create_time", "update_time"}))
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

        # Save Guardrail Provider Responses
        for provider, response in guardrail_provider_response.items():
            gr_resp_model = GRProviderResponseModel(guardrail_id=guardrail.id, guardrail_provider=provider,
                                                    response_data=response)
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
        # Validate the request
        await self.guardrail_request_validator.validate_read_request(id)

        # Fetch all guardrails matching the given ID
        guardrails = await self.gr_view_repository.get_all(filters={"guardrail_id": id})
        if not guardrails:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Guardrail", "id", [id]))

        # Initialize the result GuardrailView based on the first record
        result = GuardrailView.model_validate(guardrails[0])
        result.id = guardrails[0].guardrail_id
        result.guardrail_configs = []
        result.guardrail_provider_response = {}
        result.guardrail_connections = {}
        # result.guardrail_applications = []

        # Populate guardrail configurations and connections
        for guardrail in guardrails:
            gr_config = GRConfigView.model_validate(guardrail)
            result.guardrail_configs.append(gr_config)
            result.guardrail_connections[guardrail.guardrail_provider] = guardrail.guardrail_connection

        # TODO: uncomment when we have other details of applications like name, id to send in the response
        # Populate guardrail applications
        # guardrail_applications = await self.gr_app_repository.get_all(filters={"guardrail_id": id})
        # for gr_app in guardrail_applications:
        #     gr_application = GRApplicationView.model_validate(gr_app)
        #     result.guardrail_applications.append(gr_application)

        return result

    async def get_all_by_app_key(self, app_key: str) -> List[GuardrailView]:
        """
        Retrieve Guardrails by their AI application key.

        Args:
            app_key (str): The AI application key of the Guardrail to retrieve.

        Returns:
            List[GuardrailView]: List of Guardrail view objects corresponding to the application key.
        """
        # Retrieve all guardrails matching the application key
        guardrails = await self.gr_view_repository.get_all(filters={"application_keys": app_key})

        # Raise exception if no guardrails are found
        if not guardrails:
            raise NotFoundException(
                get_error_message(ERROR_RESOURCE_NOT_FOUND, "Guardrail", "application key", [app_key])
            )

        # Initialize a dictionary to store guardrails by their ID
        result: Dict[int, GuardrailView] = {}

        # Iterate over the guardrails and process them
        for guardrail in guardrails:
            # Validate and get the GuardrailView object
            guardrail_view = GuardrailView.model_validate(guardrail)
            guardrail_id = guardrail.guardrail_id
            guardrail_view.application_keys = None

            # Check if guardrail ID is already in the result, if not, initialize it
            if guardrail_id not in result:
                guardrail_view.id = guardrail_id
                guardrail_view.guardrail_configs = []
                guardrail_view.guardrail_provider_response = {}
                guardrail_view.guardrail_connections = {}
                result[guardrail_id] = guardrail_view  # Add it to the result

            # Add configuration, provider response, and connection to the guardrail
            gr_config = GRConfigView.model_validate(guardrail)
            result[guardrail_id].guardrail_configs.append(gr_config)
            result[guardrail_id].guardrail_provider_response[guardrail.guardrail_provider] = guardrail.guardrail_provider_response
            result[guardrail_id].guardrail_connections[guardrail.guardrail_provider] = guardrail.guardrail_connection

        # Return the list of guardrails
        return list(result.values())

    async def update(self, id: int, request: GuardrailView) -> GuardrailView:
        """
        Update a Guardrail identified by its ID.

        Args:
            id (int): The ID of the Guardrail to update.
            request (GuardrailView): The updated view object representing the Guardrail.

        Returns:
            GuardrailView: The updated Guardrail view object.
        """
        # Validate the update request
        await self.guardrail_request_validator.validate_update_request(id, request)

        # Fetch the current guardrail record by ID
        guardrail = await self.repository.get_record_by_id(id)

        # Update attributes from the request (excluding specific fields)
        guardrail.set_attribute(request.model_dump(exclude={"create_time", "update_time", "version"}))
        guardrail.version += 1  # Increment version number

        # Update guardrail in the database
        updated_gr_model = await self.repository.update_record(guardrail)
        updated_guardrail = GuardrailView.model_validate(updated_gr_model)

        # Process Guardrail Applications
        await self._update_guardrail_application_associations(id, set(request.application_keys), updated_guardrail)

        # Process Guardrail Configs
        await self._update_guardrail_configs(id, request.guardrail_configs, updated_guardrail)

        return updated_guardrail

    async def _update_guardrail_application_associations(self, guardrail_id: int, request_app_keys: Set[str],
                                                         updated_guardrail: GuardrailView):
        """Helper method to add/delete Guardrail Application associations."""
        updated_guardrail.guardrail_applications = []

        # Fetch existing applications
        gr_apps = await self.gr_app_repository.get_all(filters={"guardrail_id": guardrail_id})
        gr_app_map = {gr_app.application_key: gr_app for gr_app in gr_apps}

        # Determine which guardrail to application associations to delete and add
        existing_app_keys = set(gr_app_map.keys())
        gr_apps_to_delete = existing_app_keys - request_app_keys  # Applications to delete
        gr_apps_to_add = request_app_keys - existing_app_keys  # Applications to add

        # Delete the guardrail to application associations not in the request
        for gr_app_key in gr_apps_to_delete:
            await self.gr_app_repository.delete_record(gr_app_map[gr_app_key])

        # Add new guardrail to application associations
        for app_key in gr_apps_to_add:
            new_gr_app_model = GRApplicationModel(guardrail_id=guardrail_id, application_key=app_key)
            # Fetch and set other required fields like app name, app id by getting data from gov service
            updated_gr_app = await self.gr_app_repository.create_record(new_gr_app_model)
            updated_guardrail.guardrail_applications.append(updated_gr_app)

    async def _update_guardrail_configs(self, guardrail_id: int, request_gr_configs: List[GRConfigView],
                                        updated_guardrail: GuardrailView):
        """Helper method to update Guardrail Configs."""
        updated_guardrail.guardrail_configs = []

        # Fetch existing configurations
        gr_configs = await self.gr_config_repository.get_all(filters={"guardrail_id": guardrail_id})
        gr_config_map = {gr_config.id: gr_config for gr_config in gr_configs}

        # Determine configs to delete and update
        existing_config_ids = set(gr_config_map.keys())
        request_config_ids = {gr_config.id for gr_config in request_gr_configs}
        gr_configs_to_delete = existing_config_ids - request_config_ids

        # Delete configurations not in the request
        for gr_config_id in gr_configs_to_delete:
            await self.gr_config_repository.delete_record(gr_config_map[gr_config_id])

        # Add or update configurations
        for req_gr_config in request_gr_configs:
            gr_config_model = gr_config_map.get(req_gr_config.id)
            if gr_config_model is None:
                gr_config_model = GRConfigModel(guardrail_id=guardrail_id)

            # Set attributes from the request
            gr_config_model.set_attribute(req_gr_config.model_dump(exclude={"create_time", "update_time"}))

            # Determine whether to create or update
            if gr_config_model.id is None:
                updated_gr_config = await self.gr_config_repository.create_record(gr_config_model)
            else:
                updated_gr_config = await self.gr_config_repository.update_record(gr_config_model)

            updated_guardrail.guardrail_configs.append(GRConfigView.model_validate(updated_gr_config))

    async def delete(self, id: int):
        """
        Delete a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        await self.guardrail_request_validator.validate_delete_request(id)
        await self.delete_record(id)
