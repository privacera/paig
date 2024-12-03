import copy
from typing import List, Dict, Set

import sqlalchemy
from paig_common.lru_cache import LRUCache

from api.guardrails.api_schemas.gr_connection import GRConnectionFilter, GRConnectionView
from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter, GRConfigView, GRApplicationView, \
    GuardrailsDataView
from api.guardrails import GuardrailProvider, GuardrailConfigType
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRConfigModel, \
    GRProviderResponseModel, GRApplicationModel, GRApplicationVersionModel, GRConnectionMappingModel
from api.guardrails.database.db_operations.guardrail_repository import \
    GRConfigRepository, GRProviderResponseRepository, GuardrailRepository, GuardrailViewRepository, \
    GRApplicationRepository, GRApplicationVersionRepository
from api.guardrails.providers import GuardrailProviderManager, CreateGuardrailRequest, DeleteGuardrailRequest
from api.guardrails.services.gr_connections_service import GRConnectionService
from api.guardrails.transformers.guardrail_transform_processor import GuardrailTransformerProcessor
from core.config import load_config_file
from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import BadRequestException, NotFoundException, InternalServerError
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_ALREADY_EXISTS, \
    ERROR_RESOURCE_NOT_FOUND, ERROR_FIELD_REQUIRED, ERROR_ALLOWED_VALUES
from core.utils import validate_id, validate_string_data, validate_boolean, SingletonDepends

config = load_config_file()


def get_gr_app_version_cache_config() -> dict | None:
    if "guardrail" in config and "application_version" in config["guardrail"]:
        return config["guardrail"]["application_version"]
    else:
        return {
            "cache_capacity": 100,
            "cache_max_idle_time": 300,
            "cache_cleanup_interval_sec": 60
        }


gr_app_version_cache_config = get_gr_app_version_cache_config()

gr_app_version_cache_wrapper_dict = LRUCache(
    cache_name='guardrail-application-version-cache',
    capacity=gr_app_version_cache_config['cache_capacity'],
    max_idle_time=gr_app_version_cache_config['cache_max_idle_time'],
    cleanup_interval_sec=gr_app_version_cache_config['cache_cleanup_interval_sec']
)


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
        self.validate_configs(request)
        await self.validate_guardrail_not_exists_by_name(request.name)

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
        self.validate_configs(request.guardrail_configs)
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
        validate_string_data(name, "AI Application name")

    def validate_description(self, description: str):
        """
        Validate the description of a Guardrail.

        Args:
            description (str): The description of the Guardrail.
        """
        validate_string_data(description, "AI Application description", required=False, max_length=4000)

    async def validate_guardrail_not_exists_by_name(self, name: str):
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

    def validate_configs(self, guardrail):
        """
        Validate the Guardrail configurations.

        Args:
            guardrail (GuardrailView): The Guardrail view object containing the configurations.
        """
        if not guardrail.guardrail_configs:
            raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, "Guardrail Configurations"))
        gr_config_types = []
        gr_config_providers = []
        for gr_config in guardrail.guardrail_configs:
            if gr_config.guardrail_provider not in guardrail.enabled_providers and \
                    not (gr_config.guardrail_provider == GuardrailProvider.MULTIPLE and gr_config.config_type == GuardrailConfigType.CONTENT_MODERATION):
                raise BadRequestException(
                    f"Guardrail provider {[gr_config.guardrail_provider.name]} not enabled for the Guardrail")
            gr_config_providers.append(gr_config.guardrail_provider)
            if gr_config.config_type in gr_config_types:
                raise BadRequestException(f"Multiple Guardrail configurations of same type {[gr_config.config_type.value]} not allowed")
            gr_config_types.append(gr_config.config_type)


class GuardrailService(BaseController[GuardrailModel, GuardrailView]):

    def __init__(self,
                 guardrail_repository: GuardrailRepository = SingletonDepends(GuardrailRepository),
                 gr_app_repository: GRApplicationRepository = SingletonDepends(GRApplicationRepository),
                 gr_app_version_repository: GRApplicationVersionRepository = SingletonDepends(GRApplicationVersionRepository),
                 gr_config_repository: GRConfigRepository = SingletonDepends(GRConfigRepository),
                 gr_provider_response_repository: GRProviderResponseRepository = SingletonDepends(
                     GRProviderResponseRepository),
                 gr_view_repository: GuardrailViewRepository = SingletonDepends(GuardrailViewRepository),
                 guardrail_request_validator: GuardrailRequestValidator = SingletonDepends(GuardrailRequestValidator),
                 guardrail_connection_service: GRConnectionService = SingletonDepends(GRConnectionService)):
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
        self.gr_app_version_repository = gr_app_version_repository
        self.gr_config_repository = gr_config_repository
        self.gr_provider_response_repository = gr_provider_response_repository
        self.gr_view_repository = gr_view_repository
        self.guardrail_connection_service = guardrail_connection_service

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
        try:
            request.enabled_providers = [GuardrailProvider[provider] for provider in request.guardrail_connections.keys()]
        except KeyError as e:
            raise BadRequestException(get_error_message(ERROR_ALLOWED_VALUES, "Guardrail provider", list(e.args), [member.value for member in GuardrailProvider]))
        await self.guardrail_request_validator.validate_create_request(request)

        # Create the Guardrail
        guardrail_model = GuardrailModel()
        guardrail_model.set_attribute(request.model_dump(exclude={"create_time", "update_time", "version"}))
        guardrail = await self.repository.create_record(guardrail_model)

        # Create Guardrail Application association by updating the version
        app_keys = set(request.application_keys)
        guardrail.guardrail_applications = await self._create_guardrail_application_association(guardrail.id, app_keys)

        # bump up the version for guardrail applications
        await self._bump_up_version_in_gr_apps(app_keys)

        # Create Guardrail Configs
        guardrails_configs_list = []
        for gr_config in request.guardrail_configs:
            gr_config_model = GRConfigModel(guardrail_id=guardrail.id)
            gr_config_model.set_attribute(gr_config.model_dump(exclude={"create_time", "update_time"}))
            gr_conf = await self.gr_config_repository.create_record(gr_config_model)
            guardrails_configs_list.append(GRConfigView.model_validate(gr_conf))

        # Get Guardrail Connections
        guardrails_connection_list = await self._create_guardrail_connection_association(guardrail.id, request.guardrail_connections)

        guardrail_configs_to_create = GuardrailTransformerProcessor.process(guardrail_configs=guardrails_configs_list)

        # Create Guardrails in end service and save the Responses
        create_guardrail_response = await self._create_guardrail_to_external_provider(guardrail,
                                                                                      guardrails_connection_list,
                                                                                      guardrail_configs_to_create)

        result = GuardrailView(**request.dict())
        result.id = guardrail.id
        result.status = guardrail.status
        result.create_time = guardrail.create_time
        result.update_time = guardrail.update_time
        result.guardrail_provider_response = create_guardrail_response

        return result

    async def _create_guardrail_connection_association(self, guardrail_id, guardrail_connections):
        conn_filter = GRConnectionFilter(name=','.join(value["connectionName"] for value in guardrail_connections.values()))
        gr_conn_list = await self.guardrail_connection_service.get_all(conn_filter)
        if not gr_conn_list:
            raise BadRequestException("Guardrail Connections not found")
        for gr_conn in gr_conn_list:
            gr_conn_mapping = GRConnectionMappingModel(guardrail_id=guardrail_id, gr_connection_id=gr_conn.id, guardrail_provider=gr_conn.guardrail_provider)
            await self.guardrail_connection_service.create_guardrail_connection_mapping(gr_conn_mapping)
        return {gr_conn.guardrail_provider.name: GRConnectionView.model_validate(gr_conn).to_guardrail_connection() for gr_conn in gr_conn_list}

    async def _create_guardrail_application_association(self, guardrail_id, application_keys: Set[str]):
        # Create Guardrail Applications
        created_gr_apps = []
        for gr_app_key in application_keys:
            gr_app_model = GRApplicationModel(application_key=gr_app_key, guardrail_id=guardrail_id)
            created_gr_app = await self.gr_app_repository.create_record(gr_app_model)
            created_gr_apps.append(GRApplicationView.model_validate(created_gr_app))

        return created_gr_apps

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
        result.guardrail_connections = {}

        # Populate guardrail configurations and connections
        for guardrail in guardrails:
            gr_config = GRConfigView.model_validate(guardrail)
            result.guardrail_configs.append(gr_config)

        gr_connections = await self.guardrail_connection_service.get_connections_by_guardrail_id(id)
        result.guardrail_connections = {gr_conn.guardrail_provider: {"connectionName": gr_conn.name} for gr_conn in gr_connections}

        # TODO: Uncomment below code once we have application data fetched from gov service to here
        # Populate guardrail applications
        # result.guardrail_applications = []
        # guardrail_applications = await self.gr_app_repository.get_all(filters={"guardrail_id": id})
        # for gr_app in guardrail_applications:
        #     gr_application = GRApplicationView.model_validate(gr_app)
        #     result.guardrail_applications.append(gr_application)

        return result

    async def get_all_by_app_key(self, app_key: str, last_known_version: int = None) -> GuardrailsDataView:
        """
        Retrieve Guardrails by their AI application key.

        Args:
            app_key (str): The AI application key of the Guardrail to retrieve.
            last_known_version (int): The last known version to compare against.

        Returns:
            GuardrailsDataView: The view object containing the app_key, version and list of Guardrails.
        """
        # Check if the application key is in the cache
        cached_version = gr_app_version_cache_wrapper_dict.get(app_key)
        if last_known_version is not None:
            if cached_version is not None and cached_version <= last_known_version:
                return GuardrailsDataView(app_key=app_key, version=cached_version)

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
            result[guardrail_id].guardrail_provider_response[
                guardrail.guardrail_provider] = guardrail.guardrail_provider_response
            result[guardrail_id].guardrail_connections[guardrail.guardrail_provider] = guardrail.guardrail_connection

        # Check if the application key and version is in the cache and update the cache if not
        if cached_version is None:
            gr_app_version = await self.gr_app_version_repository.get_by(filters={"application_key": app_key})
            if gr_app_version:
                cached_version = gr_app_version[0].version
                gr_app_version_cache_wrapper_dict.put(app_key, cached_version)

        # Return the result
        return GuardrailsDataView(app_key=app_key, version=cached_version, guardrails=list(result.values()))

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
        # TODO: Set below value in updated_guardrail.guardrail_applications after fetching app data from gov service
        await self._update_guardrail_application_associations(id, set(request.application_keys))

        # Process Guardrail Configs
        await self._update_guardrail_configs(request.guardrail_configs, updated_guardrail)

        return updated_guardrail

    async def _update_guardrail_application_associations(self, guardrail_id: int, request_app_keys: Set[str]):
        """Helper method to add/delete Guardrail Application associations."""
        # Fetch existing applications
        gr_apps = await self.gr_app_repository.get_all(filters={"guardrail_id": guardrail_id})
        gr_app_map = {gr_app.application_key: gr_app for gr_app in gr_apps}

        # Determine which guardrail to application associations to delete and add
        existing_app_keys = set(gr_app_map.keys())
        all_gr_app_keys = set(request_app_keys | existing_app_keys)
        gr_apps_to_delete = existing_app_keys - request_app_keys
        gr_apps_to_add = request_app_keys - existing_app_keys
        gr_apps_unchanged = request_app_keys - gr_apps_to_add

        # Delete the guardrail to application associations not in the request
        for gr_app_key in gr_apps_to_delete:
            await self.gr_app_repository.delete_record(gr_app_map[gr_app_key])

        # Create new guardrail to application associations
        created_gr_apps = await self._create_guardrail_application_association(guardrail_id, gr_apps_to_add)

        # update the version for other guardrail to application association
        updated_gr_apps = [GRApplicationView.model_validate(gr_app) for gr_app_key, gr_app in gr_app_map.items() if
                           gr_app_key in gr_apps_unchanged]
        guardrail_applications = updated_gr_apps + created_gr_apps

        # Bump up the version of the all guardrail applications
        await self._bump_up_version_in_gr_apps(all_gr_app_keys)

        return guardrail_applications

    async def _bump_up_version_in_gr_apps(self, application_keys: Set[str]):
        updated_app_keys = set()
        filters = {"application_key": ','.join(application_keys)}
        gr_apps_version_to_bump = await self.gr_app_version_repository.get_all(filters=filters)

        # Bump-up the version for the applications
        for gr_app_version in gr_apps_version_to_bump:
            gr_app_version.version += 1
            await self.gr_app_version_repository.update_record(gr_app_version)
            gr_app_version_cache_wrapper_dict.put(gr_app_version.application_key, gr_app_version.version)
            updated_app_keys.add(gr_app_version.application_key)

        # Create new versions for the applications not in the database
        for app_key in application_keys:
            if app_key not in updated_app_keys:
                gr_app_version = GRApplicationVersionModel(application_key=app_key, version=1)
                await self.gr_app_version_repository.create_record(gr_app_version)
                gr_app_version_cache_wrapper_dict.put(app_key, 1)

    async def _update_guardrail_configs(self, request_gr_configs: List[GRConfigView],
                                        guardrail: GuardrailView):
        """Helper method to update Guardrail Configs."""
        updated_guardrail_configs = []

        # Fetch existing configurations
        gr_configs = await self.gr_config_repository.get_all(filters={"guardrail_id": guardrail.id})
        gr_config_map = {gr_config.id: gr_config for gr_config in gr_configs}

        existing_gr_configs = copy.deepcopy(gr_configs)

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
                gr_config_model = GRConfigModel(guardrail_id=guardrail.id)

            # Set attributes from the request
            gr_config_model.set_attribute(req_gr_config.model_dump(exclude={"create_time", "update_time"}))

            # Determine whether to create or update
            if gr_config_model.id is None:
                updated_gr_config = await self.gr_config_repository.create_record(gr_config_model)
            else:
                updated_gr_config = await self.gr_config_repository.update_record(gr_config_model)

            updated_guardrail_configs.append(GRConfigView.model_validate(updated_gr_config))

        guardrail.guardrail_configs = updated_guardrail_configs

        # Update Guardrail provider and update provider responses
        await self._update_guardrail_providers(existing_gr_configs, updated_guardrail_configs, guardrail)

        return updated_guardrail_configs

    async def _update_guardrail_providers(self, existing_gr_configs: List[GRConfigView],
                                          updated_gr_configs: List[GRConfigView], guardrail: GuardrailView):
        created_connections = {}
        updated_connections = {}
        deleted_connections = {}
        create_guardrails_configs_list = []
        update_guardrails_configs_list = []

        # Prepare config maps for existing and updated configurations
        existing_gr_configs_map = self.prepare_gr_provider_config_map(existing_gr_configs)
        updated_gr_configs_map = self.prepare_gr_provider_config_map(updated_gr_configs)

        # Iterate over updated config map to find created and updated connections and configs
        self._populate_created_updated_connections_configs(existing_gr_configs_map, updated_gr_configs_map,
                                                           create_guardrails_configs_list, created_connections,
                                                           update_guardrails_configs_list, updated_connections)

        # Find connections and configs to delete (existing but not in updated)
        self._populate_deleted_connections_configs(existing_gr_configs_map, updated_gr_configs_map, deleted_connections)

        # Get Guardrail Connections for all created, updated, and deleted connections
        all_conn_names = set(created_connections.values()) | set(updated_connections.values()) | set(
            deleted_connections.values())
        all_gr_connections = await self._get_guardrail_connections(all_conn_names)

        # Get connections to add, update, and delete from the list of all connections
        create_connection_list, update_connection_list, delete_connection_list = self._get_connection_to_add_update_delete(
            all_gr_connections, created_connections, updated_connections, deleted_connections)

        # Get responses to update and delete guardrails
        response_to_update_guardrail, response_to_delete_guardrail = await self._get_responses_to_update_delete(
            guardrail.id, updated_connections, deleted_connections)

        # Delete the guardrails in end service
        if delete_connection_list:
            self._delete_guardrail_to_external_provider(delete_connection_list, response_to_delete_guardrail)

        # Create guardrails in end service and save the responses
        guardrail_response = {}
        if create_connection_list and create_guardrails_configs_list:
            guardrail_response.update(await self._create_guardrail_to_external_provider(
                guardrail, create_connection_list, create_guardrails_configs_list))

        # Update guardrails in end service and save the responses
        if update_connection_list and update_guardrails_configs_list:
            guardrail_response.update(await self._update_guardrail_to_external_provider(
                guardrail, update_connection_list, update_guardrails_configs_list, response_to_update_guardrail))

        return guardrail_response

    def _delete_guardrail_to_external_provider(self, guardrail, guardrail_connections,
                                               guardrails_configs, resp_data):
        try:
            delete_guardrail_map = {}
            for provider, configs in guardrails_configs.items():
                delete_bedrock_guardrails_request = DeleteGuardrailRequest(
                    name=guardrail.name,
                    description=guardrail.description,
                    connectionDetails=guardrail_connections[provider],
                    guardrailConfigs=configs,
                    remoteGuardrailDetails=resp_data[provider]
                )
                delete_guardrail_map[provider] = delete_bedrock_guardrails_request
            GuardrailProviderManager.delete_guardrail(delete_guardrail_map)
        except Exception as e:
            raise InternalServerError(f"Failed to delete guardrails. Error - {e.__str__()}")

    async def _update_guardrail_to_external_provider(self, guardrail, update_connection_list,
                                                     update_guardrails_configs_list, response_to_update_guardrail):
        resp_data = {provider: response.response_data for provider, response in response_to_update_guardrail.items()}
        try:
            update_guardrail_response = GuardrailProviderManager.update_guardrail(
                update_connection_list, resp_data, update_guardrails_configs_list,
                name=guardrail.name, description=guardrail.description)
        except Exception as e:
            raise InternalServerError(f"Failed to update guardrails. Error - {e.__str__()}")
        for provider, response in update_guardrail_response.items():
            if not response['success']:
                raise InternalServerError(
                    f"Failed to update guardrail in provider {provider}",
                    response['response']['details'])
            gr_resp_model = response_to_update_guardrail.get(provider)
            gr_resp_model.response_data = response
            await self.gr_provider_response_repository.update_record(gr_resp_model)
        return update_guardrail_response

    async def _create_guardrail_to_external_provider(self, guardrail, guardrail_connections,
                                                     guardrails_configs):
        try:
            create_guardrails_request_map = {}
            for provider, configs in guardrails_configs.items():
                create_bedrock_guardrails_request = CreateGuardrailRequest(
                    name=guardrail.name,
                    description=guardrail.description,
                    connectionDetails=guardrail_connections[provider].connectionDetails,
                    guardrailConfigs=configs
                )
                create_guardrails_request_map[provider] = create_bedrock_guardrails_request
            create_guardrail_response = GuardrailProviderManager.create_guardrail(create_guardrails_request_map)
        except Exception as e:
            raise InternalServerError(f"Failed to create guardrails. Error - {e.__str__()}")

        for provider, response in create_guardrail_response.items():
            if not response['success']:
                raise InternalServerError(
                    f"Failed to create guardrail in external service for provider {provider}",
                    response['response']['details'])
            gr_resp_model = GRProviderResponseModel(guardrail_id=guardrail.id, guardrail_provider=provider,
                                                    response_data=response)
            await self.gr_provider_response_repository.create_record(gr_resp_model)

        return create_guardrail_response

    async def _get_responses_to_update_delete(self, guardrail_id, updated_connections, deleted_connections):
        response_to_delete_guardrail = {}
        response_to_update_guardrail = {}
        gr_response_list = await self.gr_provider_response_repository.get_all(filters={"guardrail_id": guardrail_id})
        for gr_resp in gr_response_list:
            if gr_resp.guardrail_provider.name in deleted_connections:
                response_to_delete_guardrail[gr_resp.guardrail_provider.name] = gr_resp
            if gr_resp.guardrail_provider.name in updated_connections:
                response_to_update_guardrail[gr_resp.guardrail_provider.name] = gr_resp
        return response_to_update_guardrail, response_to_delete_guardrail

    def _get_connection_to_add_update_delete(self, gr_connections, created_connections, updated_connections,
                                             deleted_connections):
        create_connection_list = []
        update_connection_list = []
        delete_connection_list = []
        for gr_conn in gr_connections:
            if gr_conn.name in created_connections.values():
                create_connection_list.append(gr_conn)
            elif gr_conn.name in updated_connections.values():
                update_connection_list.append(gr_conn)
            elif gr_conn.name in deleted_connections.values():
                delete_connection_list.append(gr_conn)
        return create_connection_list, update_connection_list, delete_connection_list

    def _populate_deleted_connections_configs(self, existing_gr_configs_map, updated_gr_configs_map,
                                              deleted_connections):
        for provider, existing_configs in existing_gr_configs_map.items():
            if provider not in updated_gr_configs_map:
                # All connections should be deleted
                deleted_connections[provider] = existing_configs[0].guardrail_provider_connection_name
            else:
                # Compare existing and updated configurations to find deleted connections
                updated_configs = updated_gr_configs_map[provider]
                updated_conf_conn_name = updated_configs[0].guardrail_provider_connection_name
                existing_conf_conn_name = existing_configs[0].guardrail_provider_connection_name

                # Connections to delete
                if existing_conf_conn_name != updated_conf_conn_name:
                    deleted_connections[provider] = existing_conf_conn_name

    def _populate_created_updated_connections_configs(self, existing_gr_configs_map, updated_gr_configs_map,
                                                      create_guardrails_configs_list, created_connections,
                                                      update_guardrails_configs_list, updated_connections):
        for provider, updated_configs in updated_gr_configs_map.items():
            updated_gr_config = [gr_config.to_guardrail_config() for gr_config in updated_configs]
            if provider not in existing_gr_configs_map:
                # All connections are new (to create)
                created_connections[provider] = updated_configs[0].guardrail_provider_connection_name
                create_guardrails_configs_list.extend(updated_gr_config)
            else:
                # Compare existing and updated configurations to find updated connections
                existing_configs = existing_gr_configs_map[provider]
                existing_conf_conn_name = existing_configs[0].guardrail_provider_connection_name
                updated_conf_conn_name = updated_configs[0].guardrail_provider_connection_name

                # Connections to update
                if existing_conf_conn_name == updated_conf_conn_name:
                    updated_connections[provider] = updated_conf_conn_name
                    update_guardrails_configs_list.extend(updated_gr_config)
                else:
                    created_connections[provider] = updated_conf_conn_name
                    create_guardrails_configs_list.extend(updated_gr_config)

    def prepare_gr_provider_config_map(self, gr_configs: List[GRConfigView]) -> Dict[str, List[GRConfigView]]:
        from collections import defaultdict
        gr_provider_configs_map = defaultdict(list)
        for gr_config in gr_configs:
            gr_provider_configs_map[gr_config.guardrail_provider].append(gr_config)
        return dict(gr_provider_configs_map)

    async def delete(self, id: int):
        """
        Delete a Guardrail by its ID.

        Args:
            id (int): The ID of the Guardrail to delete.
        """
        await self.guardrail_request_validator.validate_delete_request(id)

        # Fetch the existing Guardrail applications for the given ID
        gr_apps = await self.gr_app_repository.get_all(filters={"guardrail_id": id})
        gr_app_keys = {gr_app.application_key for gr_app in gr_apps}
        await self._bump_up_version_in_gr_apps(gr_app_keys)

        # Delete Guardrails from end service
        guardrail = await self.repository.get_record_by_id(id)
        gr_configs = await self.gr_config_repository.get_all(filters={"guardrail_id": id})
        guardrail_configs_to_delete = GuardrailTransformerProcessor.process(guardrail_configs=gr_configs)
        gr_connections = await self.guardrail_connection_service.get_connections_by_guardrail_id(id)
        connections_to_delete_guardrails = {gr_conn.guardrail_provider: gr_conn.connection_details for gr_conn in gr_connections}
        response_to_update_guardrail, response_to_delete_guardrail = await self._get_responses_to_update_delete(id, {}, connections_to_delete_guardrails)
        resp_data = {provider: response.response_data for provider, response in response_to_delete_guardrail.items()}
        self._delete_guardrail_to_external_provider(guardrail, connections_to_delete_guardrails, guardrail_configs_to_delete, resp_data)

        # Delete the Guardrail
        await self.delete_record(id)
