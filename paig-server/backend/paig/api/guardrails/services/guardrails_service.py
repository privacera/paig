import copy
import re
from typing import List

import sqlalchemy

from api.governance.api_schemas.ai_app import GuardrailApplicationsAssociation
from api.governance.services.ai_app_service import AIAppService
from api.guardrails import model_to_dict, dict_to_model
from api.guardrails.api_schemas.gr_connection import GRConnectionFilter, GRConnectionView
from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, \
    GRVersionHistoryFilter, GRVersionHistoryView
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRVersionHistoryModel
from api.guardrails.database.db_operations.guardrail_repository import GuardrailRepository, \
    GRVersionHistoryRepository
from api.guardrails.providers import GuardrailProviderManager, CreateGuardrailRequest, DeleteGuardrailRequest, \
    UpdateGuardrailRequest
from api.guardrails.services.gr_connections_service import GRConnectionService
from api.guardrails.transformers.guardrail_transformer import GuardrailTransformer
from core.config import load_config_file
from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable, create_pageable_response
from core.exceptions import BadRequestException, NotFoundException, InternalServerError
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS, \
    ERROR_RESOURCE_NOT_FOUND, ERROR_FIELD_REQUIRED
from core.utils import validate_id, validate_string_data, validate_boolean, SingletonDepends

config = load_config_file()


class GuardrailRequestValidator:
    """
    Validator class for validating Guardrail requests.

    Args:
        guardrail_repository (GuardrailRepository): The repository handling Guardrail database operations.
    """

    def __init__(self,
                 guardrail_repository: GuardrailRepository = SingletonDepends(GuardrailRepository)):
        self.guardrail_repository = guardrail_repository

    async def validate_create_request(self, request: GuardrailView):
        """
        Validate a create request for a Guardrail.

        Args:
            request (GuardrailView): The view object representing the Guardrail to create.
        """
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        self.validate_guardrail_provider_connection(request)
        self.validate_configs(request)
        await self.validate_guardrail_name_availability(request.name)

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
        self.validate_guardrail_provider_connection(request)
        self.validate_configs(request)
        await self.validate_guardrail_exists_by_id(id)

        guardrail = await self.get_guardrail_by_name(request.name)
        if guardrail is not None and guardrail.id != id:
            raise BadRequestException(get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Guardrail", "name",
                                                        [request.name]))

    async def validate_guardrail_exists_by_id(self, id):
        try:
            await self.guardrail_repository.get_record_by_id(id)
        except sqlalchemy.exc.NoResultFound as e:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Guardrail", "ID", [id]))

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
        validate_string_data(name, "Guardrail name")

    def validate_description(self, description: str):
        """
        Validate the description of a Guardrail.

        Args:
            description (str): The description of the Guardrail.
        """
        validate_string_data(description, "Guardrail description", required=False, max_length=4000)

    async def validate_guardrail_name_availability(self, name: str):
        """
        Validate the availability of a Guardrail name.

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

    def validate_configs(self, guardrail):
        """
        Validate the Guardrail configurations.

        Args:
            guardrail (GuardrailView): The Guardrail view object containing the configurations.
        """
        if not guardrail.guardrail_configs:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Guardrail Configurations"))
        gr_config_types = []
        for gr_config in guardrail.guardrail_configs:
            if gr_config.config_type in gr_config_types:
                raise BadRequestException(
                    f"Multiple Guardrail configurations of same type {[gr_config.config_type.value]} not allowed")
            gr_config_types.append(gr_config.config_type)

    def validate_guardrail_provider_connection(self, request):
        """
        Validate the Guardrail provider and connection.
        This condition ensures that both guardrail_provider and connection are set to None
        if the user opts to use only sensitive data with the default PAIG guardrail.
        However, if a value is provided for either one, the other becomes mandatory.

        Args:
            request (GuardrailView): The Guardrail view object containing the provider and connection.
        """
        if request.guardrail_provider is not None and request.guardrail_connection_name is None:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Guardrail Connection Name"))
        if request.guardrail_provider is None and request.guardrail_connection_name is not None:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Guardrail Provider"))


class GuardrailService(BaseController[GuardrailModel, GuardrailView]):

    def __init__(self,
                 guardrail_repository: GuardrailRepository = SingletonDepends(GuardrailRepository),
                 gr_version_history_repository: GRVersionHistoryRepository = SingletonDepends(
                     GRVersionHistoryRepository),
                 guardrail_request_validator: GuardrailRequestValidator = SingletonDepends(GuardrailRequestValidator),
                 guardrail_connection_service: GRConnectionService = SingletonDepends(GRConnectionService),
                 ai_app_governance_service: AIAppService = SingletonDepends(AIAppService)):
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
        self.guardrail_connection_service = guardrail_connection_service
        self.gr_version_history_repository = gr_version_history_repository
        self.ai_app_governance_service = ai_app_governance_service

    def get_repository(self) -> GuardrailRepository:
        """
        Get the Guardrail repository.

        Returns:
            GuardrailRepository: The Guardrail repository.
        """
        return self.repository

    async def list(self, filter: GuardrailFilter = GuardrailFilter(), page_number: int = 0, size: int = 10, sort: List[str] = None) -> Pageable:
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
        if sort is None:
            sort = []
        result = await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

        # If extended is set, fetch guardrail connections and add to the response
        if filter.extended:
            connection_names = set(guardrail.guardrail_connection_name for guardrail in result.content if
                                   guardrail.guardrail_connection_name)
            gr_connections = await self.guardrail_connection_service.get_all(
                GRConnectionFilter(name=",".join(connection_names)))
            gr_conn_map = {gr_conn.name: gr_conn for gr_conn in gr_connections}

            # Fetch encryption key and add id of it to the connection details
            encryption_key = await self.get_encryption_key()
            for guardrail in result.content:
                if guardrail.guardrail_connection_name and guardrail.guardrail_connection_name in gr_conn_map:
                    guardrail.guardrail_connection_details = gr_conn_map.get(guardrail.guardrail_connection_name).connection_details
                    if encryption_key:
                        guardrail.guardrail_connection_details["encryption_key_id"] = encryption_key.id
        else:
            # Remove guardrail provider response if extended is not set
            for guardrail in result.content:
                guardrail.guardrail_provider_response = None

        return result

    async def get_encryption_key(self):
        try:
            return await self.guardrail_connection_service.get_encryption_key()
        except NotFoundException:
            # Return None if encryption key is not found
            return None

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
        guardrail_model.set_attribute(
            request.model_dump(exclude_unset=True, exclude={"create_time", "update_time", "version"}, mode="json"))
        guardrail = await self.repository.create_record(guardrail_model)

        # Checking if Guardrail Provider and Connection are set before creating Guardrails in end service
        if request.guardrail_connection_name is not None and request.guardrail_provider is not None:
            # Get Guardrail Connections
            guardrail_connections = await self._get_guardrail_connections_by_name(request.guardrail_connection_name)
            # Check if Guardrail Connection with name exists for the provider passed in the request
            if request.guardrail_provider.name not in guardrail_connections:
                raise BadRequestException(
                    f"Guardrail Connection with name {[request.guardrail_connection_name]} not found for provider {[request.guardrail_provider.name]}")

            # Transform Guardrail Configs
            guardrail_configs_to_create = GuardrailTransformer.transform(request.guardrail_provider,
                                                                         request.guardrail_configs)

            # Create Guardrails in end service and update the response in guardrail
            guardrail_response = await self._create_guardrail_to_external_provider(guardrail, guardrail_connections,
                                                                                   guardrail_configs_to_create)
            guardrail.guardrail_provider_response = guardrail_response
            guardrail = await self.repository.update_record(guardrail)

        # Save the guardrail in the history table
        await self.save_guardrail_version_history(guardrail)

        result = GuardrailView(**request.model_dump(mode="json"))
        result.id = guardrail.id
        result.status = guardrail.status
        result.create_time = guardrail.create_time
        result.update_time = guardrail.update_time

        return result

    async def save_guardrail_version_history(self, guardrail):
        guardrail_dict = model_to_dict(guardrail)
        gr_version_history = dict_to_model(guardrail_dict, GRVersionHistoryModel)
        gr_version_history.id = None
        gr_version_history.create_time = guardrail.update_time
        gr_version_history.guardrail_id = guardrail.id
        await self.gr_version_history_repository.create_record(gr_version_history)

    async def _get_guardrail_connections_by_name(self, guardrail_connection_name: str) -> dict[str, GRConnectionView]:
        gr_conn_map_by_provider = {}
        gr_conn_list = await self._get_guardrail_connections(guardrail_connection_name)
        for gr_conn in gr_conn_list:
            gr_conn_map_by_provider[gr_conn.guardrail_provider.name] = gr_conn
        return gr_conn_map_by_provider

    async def _get_guardrail_connections(self, guardrail_connection_name: str) -> List[GRConnectionView]:
        gr_conn_filter = GRConnectionFilter(name=guardrail_connection_name)
        gr_conn_list = await self.guardrail_connection_service.get_all(gr_conn_filter, True)
        if not gr_conn_list:
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_NOT_FOUND, "Guardrail Connection", "name",
                                  [guardrail_connection_name]))
        return gr_conn_list

    async def get_by_id(self, id: int, extended: bool) -> GuardrailView:
        """
        Retrieve a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to retrieve.
            extended (bool): Include extended information

        Returns:
            GuardrailView: The Guardrail view object corresponding to the ID.
        """
        # Validate the request
        await self.guardrail_request_validator.validate_read_request(id)

        # Fetch all guardrail view entries which contain same guardrail
        # we are using view here as there are multiple entries for the same guardrail with multiple config types,
        # this combined view enhance api speed and reduce database calls and that's why we are not directly using get_record_by_id method
        guardrail = await self.repository.get_record_by_id(id)

        # Initialize the result GuardrailView based on the first record
        result = GuardrailView.model_validate(guardrail)

        if extended and guardrail.guardrail_connection_name:
            # Fetch Guardrail Connections by Guardrail IDs
            gr_connections = await self.guardrail_connection_service.get_all(GRConnectionFilter(name=guardrail.guardrail_connection_name))
            result.guardrail_connection_details = gr_connections[0].connection_details if gr_connections else None

            # Fetch encryption key and add id of it to the connection details
            try:
                encryption_key = await self.guardrail_connection_service.get_encryption_key()
                if encryption_key:
                    result.guardrail_connection_details["encryption_key_id"] = encryption_key.id
            except NotFoundException:
                pass
        else:
            result.guardrail_connection_details = None
            result.guardrail_provider_response = None

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
        # Validate the update request
        await self.guardrail_request_validator.validate_update_request(id, request)

        # Fetch the current guardrail record by ID
        guardrail = await self.repository.get_record_by_id(id)
        existing_guardrail = GuardrailView.model_validate(copy.deepcopy(guardrail))

        if not self.is_record_updated(existing_guardrail, request):
            return existing_guardrail

        # Update attributes from the request (excluding specific fields)
        guardrail.set_attribute(
            request.model_dump(exclude_unset=True,
                               exclude={"name", "create_time", "update_time", "version", "guardrail_provider_response"},
                               mode="json"))

        guardrail.version += 1  # Increment version number
        if request.guardrail_provider is None and request.guardrail_connection_name is None:
            guardrail.guardrail_provider = None
            guardrail.guardrail_connection_name = None

        guardrail_view = GuardrailView.model_validate(guardrail)

        # Update Guardrail provider and update provider responses
        guardrail_response = await self._update_guardrail_providers(guardrail_view, existing_guardrail)

        # Update the response data in the guardrail
        if guardrail_response:
            guardrail.guardrail_provider_response = guardrail_response

        # Update guardrail in the database
        guardrail = await self.repository.update_record(guardrail)

        # Save the guardrail in the history table
        await self.save_guardrail_version_history(guardrail)

        guardrail_view.guardrail_provider_response = None
        return guardrail_view

    def is_record_updated(self, existing_guardrail: GuardrailView, request: GuardrailView):
        """
        Check if the record is updated.

        Args:
            existing_guardrail (GuardrailView): The existing Guardrail view object.
            request (GuardrailView): The updated view object representing the Guardrail.

        Returns:
            bool: True if record is updated else False.
        """
        if existing_guardrail.description != request.description: return True
        if request.status and existing_guardrail.status != request.status: return True
        if existing_guardrail.guardrail_provider != request.guardrail_provider: return True
        if existing_guardrail.guardrail_connection_name != request.guardrail_connection_name: return True
        return request.guardrail_configs and existing_guardrail.guardrail_configs != request.guardrail_configs

    async def _update_guardrail_providers(self, request_guardrail: GuardrailView, existing_guardrail: GuardrailView):
        guardrail_response = {}
        gr_connections_to_create = {}
        gr_connections_to_update = {}
        gr_connections_to_delete = {}
        new_guardrails_configs = {}
        existing_guardrail_configs = {}

        # Prepare config maps for existing and updated configurations
        if existing_guardrail.guardrail_provider is None and request_guardrail.guardrail_provider is None:
            return

        gr_conn_names = set()
        if request_guardrail.guardrail_provider is not None and request_guardrail.guardrail_connection_name is not None:
            new_guardrails_configs = GuardrailTransformer.transform(request_guardrail.guardrail_provider,
                                                                    request_guardrail.guardrail_configs)
            gr_conn_names.add(request_guardrail.guardrail_connection_name)
        if (existing_guardrail.guardrail_provider is not None
                and existing_guardrail.guardrail_connection_name is not None):
            existing_guardrail_configs = GuardrailTransformer.transform(existing_guardrail.guardrail_provider,
                                                                        existing_guardrail.guardrail_configs)
            gr_conn_names.add(existing_guardrail.guardrail_connection_name)

        if not gr_conn_names:
            return

        # Get guardrail connections by guardrail ID from the database
        gr_connections_list = await self._get_guardrail_connections(",".join(gr_conn_names))
        gr_connection_map = {}
        for gr_conn in gr_connections_list:
            if (gr_conn.name == request_guardrail.guardrail_connection_name
                    and gr_conn.guardrail_provider != request_guardrail.guardrail_provider):
                raise BadRequestException(
                    f"Guardrail Connection with name {[request_guardrail.guardrail_connection_name]}"
                    f" not found for provider {[request_guardrail.guardrail_provider.name]}")
            gr_connection_map[gr_conn.name] = gr_conn

        # Prepare the guardrail connections and configs to create, update, and delete
        if request_guardrail.guardrail_connection_name == existing_guardrail.guardrail_connection_name:
            if request_guardrail.guardrail_connection_name is not None:
                if new_guardrails_configs and not existing_guardrail_configs:
                    gr_connections_to_create[request_guardrail.guardrail_provider.name] = gr_connection_map[
                        request_guardrail.guardrail_connection_name]
                elif existing_guardrail_configs and not new_guardrails_configs:
                    gr_connections_to_delete[request_guardrail.guardrail_provider.name] = gr_connection_map[
                        request_guardrail.guardrail_connection_name]
                else:
                    gr_connections_to_update[request_guardrail.guardrail_provider.name] = gr_connection_map[
                        request_guardrail.guardrail_connection_name]
        else:
            if existing_guardrail.guardrail_connection_name is not None:
                gr_connections_to_delete[existing_guardrail.guardrail_provider.name] = gr_connection_map[
                    existing_guardrail.guardrail_connection_name]
            if request_guardrail.guardrail_connection_name is not None:
                gr_connections_to_create[request_guardrail.guardrail_provider.name] = gr_connection_map[
                    request_guardrail.guardrail_connection_name]

        # Delete guardrails in end service
        if gr_connections_to_delete and existing_guardrail_configs:
            await self._delete_guardrail_to_external_provider(
                request_guardrail, gr_connections_to_delete, existing_guardrail_configs,
                existing_guardrail.guardrail_provider_response)

        # Create guardrails in end service and save the responses
        if gr_connections_to_create and new_guardrails_configs:
            gr_resp_data = await self._create_guardrail_to_external_provider(request_guardrail, gr_connections_to_create,
                                                                             new_guardrails_configs)
            guardrail_response.update(gr_resp_data)

        # Update guardrails in end service and save the responses
        if gr_connections_to_update:
            gr_resp_data = await self._update_guardrail_to_external_provider(
                request_guardrail, gr_connections_to_update, new_guardrails_configs,
                existing_guardrail.guardrail_provider_response)
            guardrail_response.update(gr_resp_data)

        return guardrail_response

    async def _delete_guardrail_to_external_provider(self, guardrail, guardrail_connections,
                                                     guardrails_configs, guardrail_provider_response):
        try:
            delete_guardrail_map = {}
            for provider, configs in guardrails_configs.items():
                delete_bedrock_guardrails_request = DeleteGuardrailRequest(
                    name=self.generate_guardrail_name(guardrail.name),
                    description=guardrail.description,
                    connectionDetails=guardrail_connections[provider].connection_details,
                    guardrailConfigs=configs,
                    remoteGuardrailDetails=guardrail_provider_response[provider]
                )
                delete_guardrail_map[provider] = delete_bedrock_guardrails_request
            delete_guardrail_response = GuardrailProviderManager.delete_guardrail(delete_guardrail_map)
        except Exception as e:
            raise InternalServerError(f"Failed to delete guardrails. Error - {e.__str__()}")

        for provider, response in delete_guardrail_response.items():
            self.handle_response_for_failure(provider, response, 'delete')

        return delete_guardrail_response

    async def _update_guardrail_to_external_provider(self, guardrail, guardrail_connections,
                                                     guardrails_configs, guardrail_provider_response):
        try:
            update_guardrail_map = {}
            for provider, configs in guardrails_configs.items():
                update_bedrock_guardrails_request = UpdateGuardrailRequest(
                    name=self.generate_guardrail_name(guardrail.name),
                    description=guardrail.description,
                    connectionDetails=guardrail_connections[provider].connection_details,
                    guardrailConfigs=configs,
                    remoteGuardrailDetails=guardrail_provider_response[provider]
                )
                update_guardrail_map[provider] = update_bedrock_guardrails_request
            update_guardrail_response = GuardrailProviderManager.update_guardrail(update_guardrail_map)
        except Exception as e:
            raise InternalServerError(f"Failed to update guardrails. Error - {e.__str__()}")

        for provider, response in update_guardrail_response.items():
            self.handle_response_for_failure(provider, response, 'update')

        return update_guardrail_response

    def generate_guardrail_name(self, input_string: str) -> str:
        """
        Replace characters in the string that do not match the regex [0-9a-zA-Z-_]+ with an underscore.

        Args:
            input_string (str): The input string to process.

        Returns:
            str: The updated string with invalid characters replaced.
        """
        # Define the regex pattern for allowed characters
        pattern = r'[^0-9a-zA-Z-_]'
        # Replace characters not matching the pattern with an underscore
        updated_string = re.sub(pattern, '_', input_string)
        return updated_string

    async def _create_guardrail_to_external_provider(self, guardrail, guardrail_connections,
                                                     guardrails_configs):
        try:
            create_guardrails_request_map = {}
            for provider, configs in guardrails_configs.items():
                create_bedrock_guardrails_request = CreateGuardrailRequest(
                    name=self.generate_guardrail_name(guardrail.name),
                    description=guardrail.description,
                    connectionDetails=guardrail_connections[provider].connection_details,
                    guardrailConfigs=configs
                )
                create_guardrails_request_map[provider] = create_bedrock_guardrails_request
            create_guardrail_response = GuardrailProviderManager.create_guardrail(create_guardrails_request_map)
        except Exception as e:
            raise InternalServerError(f"Failed to create guardrails. Error - {e.__str__()}")

        for provider, response in create_guardrail_response.items():
            self.handle_response_for_failure(provider, response, 'create')

        return create_guardrail_response

    def handle_response_for_failure(self, provider, response, operation='update'):
        if not response['success']:
            if (operation == 'delete' and 'errorType' in response['response']['details'] and
                    response['response']['details']['errorType'] == 'ResourceNotFoundException'):
                return
            if response['response']['details']['errorType'] == 'ClientError':
                if 'ExpiredTokenException' in response['response']['details']['details']:
                    raise InternalServerError(
                        f"Failed to {operation} guardrail in {provider}: The security token included in the connection is expired",
                        response['response']['details'])
                error_messages = ('UnrecognizedClientException', 'InvalidSignatureException')
                if any(error in response['response']['details']['details'] for error in error_messages):
                    raise InternalServerError(
                        f"Failed to {operation} guardrail in {provider}: The associated connection details(AWS Secret Access Key) are invalid",
                        response['response']['details'])
            if response['response']['details']['errorType'] == 'AccessDeniedException':
                raise InternalServerError(
                    f"Failed to {operation} guardrail in {provider}: Access Denied for the associated connection",
                    response['response']['details'])
            raise InternalServerError(f"Failed to {operation} guardrail in {provider}", response['response']['details'])

    async def delete(self, id: int):
        """
        Delete a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        await self.guardrail_request_validator.validate_delete_request(id)

        # Fetch the existing Guardrail for the given ID
        guardrail_model = await self.repository.get_record_by_id(id)
        guardrail = GuardrailView.model_validate(guardrail_model)

        # Delete Guardrails from end service
        if guardrail.guardrail_provider is not None and guardrail.guardrail_connection_name is not None:
            guardrail_configs_to_delete = GuardrailTransformer.transform(guardrail.guardrail_provider,
                                                                         guardrail.guardrail_configs)
            connections_to_delete_guardrails = await self._get_guardrail_connections_by_name(
                guardrail.guardrail_connection_name)
            await self._delete_guardrail_to_external_provider(guardrail, connections_to_delete_guardrails,
                                                              guardrail_configs_to_delete,
                                                              guardrail_model.guardrail_provider_response)

        # Delete the Guardrail
        await self.repository.delete_record(guardrail_model)

        # Disassociated the guardrail from the applications
        await self._disassociate_guardrail_from_applications(guardrail.name)

    async def get_history(self, id, filter: GRVersionHistoryFilter, page_number: int, size: int, sort: List[str]) -> Pageable:
        """
        Get the history of a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to retrieve the history for.
            filter (GRVersionHistoryFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of items per page.
            sort (List[str]): The fields to sort by.

        Returns:
            Pageable: A paginated response containing the Guardrail version history.
        """
        if id is not None:
            # Validate the request
            validate_id(id, "Guardrail ID")
            filter.id = None
            filter.guardrail_id = id
        records, total_count = await self.gr_version_history_repository.list_records(
            filter=filter, page_number=page_number, size=size, sort=sort)
        v_records = [GRVersionHistoryView.model_validate(record) for record in records]
        return create_pageable_response(v_records, total_count, page_number, size, sort)

    async def _disassociate_guardrail_from_applications(self, guardrail_name):
        """
        Disassociate the guardrail from the applications.

        Args:
            guardrail_name (str): The name of the guardrail.
        """
        request = GuardrailApplicationsAssociation(guardrail=guardrail_name, applications=[])
        await self.ai_app_governance_service.disassociate_guardrail(request)

