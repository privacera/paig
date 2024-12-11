from typing import List, Dict, Any

from paig_common.encryption import DataEncryptor
from sqlalchemy.exc import NoResultFound

from api.encryption.api_schemas.encryption_key import EncryptionKeyView
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType
from api.encryption.events.startup import create_encryption_keys_if_not_exists
from api.encryption.services.encryption_key_service import EncryptionKeyService
from api.guardrails.api_schemas.gr_connection import GRConnectionView, GRConnectionFilter
from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails.database.db_models.guardrail_model import GRConnectionMappingModel
from api.guardrails.database.db_models.guardrail_view_model import GRConnectionViewModel
from api.guardrails.database.db_operations.gr_connection_repository import GRConnectionMappingRepository, \
    GRConnectionViewRepository
from api.guardrails.database.db_operations.gr_connection_repository import GRConnectionRepository
from api.guardrails.providers import GuardrailProviderManager, GuardrailConnection
from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.exceptions import NotFoundException, BadRequestException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND, \
    ERROR_RESOURCE_ALREADY_EXISTS
from core.utils import validate_id, SingletonDepends, validate_boolean, validate_string_data


class GRConnectionRequestValidator:

    def __init__(self, gr_connection_repository: GRConnectionRepository = SingletonDepends(GRConnectionRepository)):
        self.gr_connection_repository = gr_connection_repository

    async def validate_read_request(self, id: int):
        """
        Validate a read request for a Guardrail Connection.

        Args:
            id (int): The ID of the Guardrail Connection to retrieve.
        """
        validate_id(id, "Guardrail Connection ID")
        await self.validate_gr_connections_exists_by_id(id)

    async def validate_create_request(self, request: GRConnectionView):
        """
        Validate a create request for a Guardrail Connection.

        Args:
            request (GRConnectionView): The view object representing the Guardrail Connection to create.
        """
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        await self.validate_gr_connection_not_exists_by_name(request.name)

    async def validate_update_request(self, id: int, request: GRConnectionView):
        """
        Validate an update request for a Guardrail Connection.

        Args:
            id (int): The ID of the Guardrail Connection to update.
            request (AIApplicationView): The updated view object representing the Guardrail Connection.

        Raises:
            BadRequestException: If the ID is not a positive integer.
        """
        self.validate_status(request.status)
        self.validate_name(request.name)
        self.validate_description(request.description)
        await self.validate_gr_connections_exists_by_id(id)
        await self.validate_gr_connection_not_exists_by_name(request.name, id)

    async def validate_delete_request(self, id: int):
        """
        Validate a delete request for a Guardrail Connection.

        Args:
            id (int): The ID of the Guardrail Connection to delete.
        """
        validate_id(id, "Guardrail Connection ID")
        await self.validate_gr_connections_exists_by_id(id)

    def validate_status(self, status: int):
        """
        Validate the status of a Guardrail Connection.

        Args:
            status (int): The status of the Guardrail Connection.
        """
        validate_boolean(status, "Guardrail Connection status")

    def validate_name(self, name: str):
        """
        Validate the name of a Guardrail Connection.

        Args:
            name (str): The name of the Guardrail Connection.
        """
        validate_string_data(name, "Guardrail Connection name")

    def validate_description(self, description: str):
        """
        Validate the description of a Guardrail Connection.

        Args:
            description (str): The description of the Guardrail Connection.
        """
        validate_string_data(description, "Guardrail Connection description")

    async def validate_gr_connection_not_exists_by_name(self, name: str, id: int = None):
        """
        Validate if a Guardrail Connection exists by name.

        Args:
            name (str): The name of the Guardrail Connection.
            id (int): The ID of the Guardrail Connection.
        """
        gr_connection = await self.get_by_name(name)
        if gr_connection is not None and (id is None or gr_connection.id != id):
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_ALREADY_EXISTS, "Guardrail Connection", "name", [name]))

    async def validate_gr_connections_exists_by_id(self, id: int):
        """
        Validate if a Guardrail Connection exists by ID.

        Args:
            id (int): The ID of the Guardrail Connection.
        """
        try:
            await self.gr_connection_repository.get_record_by_id(id)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Guardrail Connection", "ID", [id]))

    async def get_by_name(self, name: str):
        """
        Get a Guardrail Connection by name.

        Args:
            name (str): The name of the Guardrail Connection.

        Returns:
            GRConnectionModel: The Guardrail Connection with the specified name.
        """
        filter = GRConnectionFilter()
        filter.name = name
        filter.exact_match = True
        records, total_count = await self.gr_connection_repository.list_records(filter=filter)
        if total_count > 0:
            return records[0]
        return None


class GRConnectionService(BaseController[GRConnectionModel, GRConnectionView]):
    """
    Service class specifically for handling Guardrail Provider Connections.

    Args:
        gr_connection_repository (GRConnectionRepository): The Guardrail Connection repository to use.
        gr_connection_request_validator (GRConnectionRequestValidator): The Guardrail Connection request validator to use.
    """

    def __init__(self, gr_connection_repository: GRConnectionRepository = SingletonDepends(GRConnectionRepository),
                 gr_connection_mapping_repository: GRConnectionMappingRepository = SingletonDepends(GRConnectionMappingRepository),
                 gr_connection_view_repository: GRConnectionViewRepository = SingletonDepends(GRConnectionViewRepository),
                 encryption_key_service: EncryptionKeyService = SingletonDepends(EncryptionKeyService),
                 gr_connection_request_validator: GRConnectionRequestValidator = SingletonDepends(GRConnectionRequestValidator)):
        super().__init__(gr_connection_repository, GRConnectionModel, GRConnectionView)
        self.gr_connection_mapping_repository = gr_connection_mapping_repository
        self.gr_connection_view_repository = gr_connection_view_repository
        self.encryption_key_service = encryption_key_service
        self.gr_connection_request_validator = gr_connection_request_validator

    def get_repository(self) -> GRConnectionRepository:
        """
        Get the Guardrail Connection repository.

        Returns:
            GRConnectionRepository: The Guardrail Connection repository.
        """
        return self.repository

    async def get_by_id(self, id: int):
        """
        Get the configuration of a Guardrail Connection by id.

        Args:
            id (int): The ID of the Guardrail Connection.

        Returns:
            GRConnectionView: The configuration of the Guardrail Connection.
        """
        await self.gr_connection_request_validator.validate_read_request(id)

        repository = self.get_repository()
        return await repository.get_record_by_id(id)

    async def create(self, request: GRConnectionView) -> GRConnectionView:
        """
        Create a new Guardrail Connection.

        Args:
            request (GRConnectionView): The view object representing the Guardrail connection to create.

        Returns:
            GRConnectionView: The created Guardrail Connection view object.
        """
        await self.gr_connection_request_validator.validate_create_request(request)
        await create_encryption_keys_if_not_exists(self.encryption_key_service, EncryptionKeyType.CRDS_PROTECT_GUARDRAIL)
        await self.encrypt_connection_details(request)

        return await self.create_record(request, exclude_fields={"encrypt_fields"})

    async def test_connection(self, request: GRConnectionView) -> Dict[str, Any]:
        """
        Test the connection of a Guardrail Connection.

        Args:
            request (GRConnectionView): The view object representing the Guardrail connection to test.

        Returns:
            Dict[str, Any]: The response of the connection test.
        """
        await self.decrypt_connection_details(request)
        guardrail_connection = GuardrailConnection(
            name=request.name,
            description=request.description,
            guardrailProvider=request.guardrail_provider,
            connectionDetails=request.connection_details
        )

        connection_test_request_dict = {
            request.guardrail_provider.name: guardrail_connection
        }
        connection_test_response_dict = GuardrailProviderManager.verify_guardrails_connection_details(connection_test_request_dict)

        return connection_test_response_dict[request.guardrail_provider.name]

    async def list(self, filter: GRConnectionFilter, page_number: int, size: int, sort: list) -> Pageable:
        """
        List Guardrail Connection configurations.

        Args:
            filter (dict): The filter to apply to the query.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (list): The sort order to apply to the query.

        Returns:
            PageableResponse: The pageable response containing the list of Guardrail Connection configurations.
        """
        return await self.list_records(filter, page_number, size, sort)

    async def list_connection_provider_names(self) -> List[str]:
        """
        Retrieve a list of Guardrail connection provider names.

        Returns:
            List[str]: A list of Guardrail connection provider names.
        """
        filter = GRConnectionFilter()
        records, total_count = await self.repository.list_records(filter=filter, cardinality="guardrail_provider")
        names = [record.guardrail_provider for record in records]
        return names

    async def get_all(self, filter: GRConnectionFilter, decrypted=False) -> List[GRConnectionView]:
        """
        Get all Guardrail Connection configurations.

        Args:
            filter (GRConnectionFilter): The filter to apply to the query.
            decrypted (bool): Whether to decrypt the connection details.

        Returns:
            List[GRConnectionView]: The list of Guardrail Connection configurations.
        """
        result = await self.repository.get_all(filter.dict())
        if decrypted:
            for connection in result:
                await self.decrypt_connection_details(connection)
        return result

    async def update(self, id: int, request: GRConnectionView):
        """
        Update the configuration of a Guardrail Connection.

        Args:
            id (int): The ID of the Guardrail Connection.
            request (GRConnectionView): The updated configuration of the Guardrail Connection.

        Returns:
            GRConnectionView: The updated configuration of the Guardrail Connection.
        """
        await self.gr_connection_request_validator.validate_update_request(id, request)
        await self.encrypt_connection_details(request)
        return await self.update_record(id, request, exclude_fields={"encrypt_fields"})

    async def delete(self, id: int):
        """
        Delete a Guardrail Connection.

        Args:
            id (int): The ID of the Guardrail Connection to delete.
        """
        await self.gr_connection_request_validator.validate_delete_request(id)
        return await self.delete_record(id)

    async def create_guardrail_connection_mapping(self, gr_conn_mapping: GRConnectionMappingModel):
        """
        Create a new Guardrail Connection Mapping.

        Args:
            gr_conn_mapping (GRConnectionMappingModel): The view object representing the Guardrail connection mapping to create.
        """
        return await self.gr_connection_mapping_repository.create_record(gr_conn_mapping)

    async def get_connections_by_guardrail_id(self, guardrail_id, decrypted=False) -> List[GRConnectionViewModel]:
        """
        Get the connections by guardrail id.

        Args:
            guardrail_id: The ID of the Guardrail.
            decrypted: Whether to decrypt the connection details.

        Returns:
            List[GRConnectionViewModel]: The list of Guardrail Connection Mappings.
        """
        result = await self.gr_connection_view_repository.get_all(filters={"guardrail_id": guardrail_id})
        if decrypted:
            for connection in result:
                await self.decrypt_connection_details(connection)
        return result

    async def get_guardrail_connection_mappings(self, guardrail_id: int) -> List[GRConnectionMappingModel]:
        """
        Get the Guardrail Connection Mapping.

        Args:
            guardrail_id (int): The ID of the Guardrail.

        Returns:
            List[GRConnectionMappingModel]: The list of Guardrail Connection Mappings.
        """
        return await self.gr_connection_mapping_repository.get_all(filters={"guardrail_id": guardrail_id})

    async def delete_guardrail_connection_mapping(self, gr_conn_mapping: GRConnectionMappingModel):
        """
        Delete the Guardrail Connection Mapping.

        Args:
            gr_conn_mapping (GRConnectionMappingModel): The view object representing the Guardrail connection mapping to delete.

        Returns:
            None
        """
        await self.gr_connection_mapping_repository.delete_record(gr_conn_mapping)

    async def encrypt_connection_details(self, gr_connection):
        connection_details = gr_connection.connection_details
        gr_creds_key: EncryptionKeyView = await self.encryption_key_service.get_active_encryption_key_by_type(
            EncryptionKeyType.CRDS_PROTECT_GUARDRAIL)
        data_encryptor = DataEncryptor(public_key=gr_creds_key.public_key, private_key=gr_creds_key.private_key)
        for key, value in connection_details.items():
            if not value.startswith("GuardrailEncrypt:") and gr_connection.encrypt_fields and key in gr_connection.encrypt_fields:
                gr_connection.connection_details[key] = "GuardrailEncrypt:" + data_encryptor.encrypt(data=str(value))

    async def decrypt_connection_details(self, gr_connection):
        connection_details = gr_connection.connection_details
        gr_creds_key: EncryptionKeyView = await self.encryption_key_service.get_active_encryption_key_by_type(
            EncryptionKeyType.CRDS_PROTECT_GUARDRAIL)
        data_encryptor = DataEncryptor(public_key=gr_creds_key.public_key, private_key=gr_creds_key.private_key)
        for key, value in connection_details.items():
            if value.startswith("GuardrailEncrypt:"):
                try:
                    gr_connection.connection_details[key] = data_encryptor.decrypt(
                        data=value.replace("GuardrailEncrypt:", ""))
                except Exception as e:
                    raise BadRequestException(
                        f"Invalid connection details('{key}') for {gr_connection.guardrail_provider.value}")