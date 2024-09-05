import logging
from typing import List
from paig_common.encryption import RSAKeyInfo, RSAKeyUtil

from core.controllers.base_controller import BaseController
from core.controllers.paginated_response import Pageable
from core.utils import validate_id, SingletonDepends
from core.exceptions import BadRequestException, NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_ALLOWED_VALUES
from api.encryption.api_schemas.encryption_key import EncryptionKeyFilter, EncryptionKeyView
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyModel, EncryptionKeyType, \
    EncryptionKeyStatus
from api.encryption.database.db_operations.encryption_key_repository import EncryptionKeyRepository
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from api.encryption.utils.secure_encryptor import SecureEncryptor


logger = logging.getLogger(__name__)


class EncryptionKeyRequestValidator:
    """
    Validator class for encryption key requests.

    Args:
        encryption_key_repository (EncryptionKeyRepository): The repository handling encryption key database operations.
    """

    def __init__(self, encryption_key_repository: EncryptionKeyRepository = SingletonDepends(EncryptionKeyRepository)):
        self.encryption_key_repository = encryption_key_repository

    # noinspection PyMethodMayBeStatic
    def validate_key_type(self, key_type: EncryptionKeyType):
        from core.utils import validate_required_data

        validate_required_data(key_type, "Key Type")

        # Check key type is valid
        if key_type not in EncryptionKeyType:
            raise BadRequestException(get_error_message(ERROR_ALLOWED_VALUES, "Key Type", [key_type],
                                                        [e.value for e in EncryptionKeyType]))

    # noinspection PyMethodMayBeStatic
    def validate_create_request(self, key_type: EncryptionKeyType):
        self.validate_key_type(key_type)

    # noinspection PyMethodMayBeStatic
    def validate_read_request(self, id: int):
        """
        Validate a read request for an encryption key.

        Args:
            id (int): The ID of the encryption key to retrieve.
        """

        validate_id(id, "Encryption Key ID")

    # noinspection PyMethodMayBeStatic
    def validate_delete_request(self, id: int):
        """
        Validate a delete request for an encryption key.

        Args:
            id (int): The ID of the encryption key to delete.
        """

        validate_id(id, "Encryption Key ID")

    # noinspection PyMethodMayBeStatic
    def validate_disable_request(self, id: int):
        """
        Validate a disable request for an encryption key.

        Args:
            id (int): The ID of the encryption key to disable.
        """

        validate_id(id, "Encryption Key ID")


class EncryptionKeyService(BaseController[EncryptionKeyModel, EncryptionKeyView]):
    """
    Service class for the encryption keys service.

    Args:
        encryption_key_repository (EncryptionKeyRepository): The repository handling encryption key database operations.
        encryption_key_request_validator (EncryptionKeyRequestValidator): The validator for encryption
    """

    def __init__(self,
                 encryption_key_repository: EncryptionKeyRepository = SingletonDepends(EncryptionKeyRepository),
                 secure_encryptor_factory: SecureEncryptorFactory = SingletonDepends(SecureEncryptorFactory),
                 encryption_key_request_validator: EncryptionKeyRequestValidator = SingletonDepends(EncryptionKeyRequestValidator)):
        super().__init__(
            encryption_key_repository,
            EncryptionKeyModel,
            EncryptionKeyView
        )
        self.secure_encryptor_factory = secure_encryptor_factory
        self.encryption_key_request_validator = encryption_key_request_validator

    def get_repository(self) -> EncryptionKeyRepository:
        """
        Retrieve the encryption key repository.

        Returns:
            EncryptionKeyRepository: The encryption key repository.
        """
        return self.repository

    async def list_encryption_keys(self, filter: EncryptionKeyFilter, page_number: int, size: int, sort: List[str]) -> (
            Pageable):
        """
        Retrieve a paginated list of encryption keys.

        Args:
            filter (EncryptionKeyFilter): Filtering criteria.
            page_number (int): Page number to retrieve.
            size (int): Number of records per page.
            sort (List[str]): List of fields to sort by.

        Returns:
            Pageable: A paginated response containing encryption key view objects and metadata.
        """
        result = await self.list_records(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()

        # Decrypt all keys
        for record in result.content:
            record.public_key = secure_encryptor.decrypt(record.public_key)
            record.private_key = secure_encryptor.decrypt(record.private_key)

        return result

    async def create_encryption_key(self, key_type: EncryptionKeyType = EncryptionKeyType.MSG_PROTECT_SHIELD) -> (
            EncryptionKeyView):
        """
        Create a new encryption key.

        Args:
            key_type (EncryptionKeyType): The type of the key to create.

        Returns:
            EncryptionKeyView: The created encryption key view object.
        """
        self.encryption_key_request_validator.validate_create_request(key_type)

        repository = self.get_repository()

        try:
            # Set existing active key to passive
            existing_encryption_key: EncryptionKeyModel = await repository.get_active_encryption_key_by_type(key_type)

            existing_encryption_key_updated_request = EncryptionKeyView.model_validate(existing_encryption_key)
            existing_encryption_key_updated_request.key_status = EncryptionKeyStatus.PASSIVE

            await self.update_record(existing_encryption_key.id, existing_encryption_key_updated_request)
        except NotFoundException:
            logger.debug(f"No active key found for key type {key_type}")

        # Create new encryption key
        rsa_key_info: RSAKeyInfo = RSAKeyUtil.generate_key_pair()

        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()

        # Encrypt the keys before storing them
        encrypted_public_key = secure_encryptor.encrypt(rsa_key_info.public_key_encoded_str)
        encrypted_private_key = secure_encryptor.encrypt(rsa_key_info.private_key_encoded_str)

        # Store encrypted keys in the database
        encryption_key_view: EncryptionKeyView = EncryptionKeyView()
        encryption_key_view.public_key = encrypted_public_key
        encryption_key_view.private_key = encrypted_private_key
        encryption_key_view.key_type = key_type
        encryption_key_view.key_status = EncryptionKeyStatus.ACTIVE

        result: EncryptionKeyView = await self.create_record(encryption_key_view)

        response: EncryptionKeyView = EncryptionKeyView()
        response.id = result.id
        response.status = result.status
        response.create_time = result.create_time
        response.update_time = result.update_time
        response.key_type = key_type
        response.key_status = result.key_status

        return response

    async def get_public_encryption_key_by_id(self, id: int) -> EncryptionKeyView:
        """
        Retrieve the public encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to retrieve.

        Returns:
            str: The public encryption key corresponding to the ID.
        """
        self.encryption_key_request_validator.validate_read_request(id)

        result: EncryptionKeyView = await self.get_record_by_id(id)

        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()

        # Decrypt the public key before returning it
        result.private_key = None
        result.public_key = secure_encryptor.decrypt(result.public_key)

        return result

    async def get_encryption_key_by_id(self, id: int) -> EncryptionKeyView:
        """
        Retrieve an encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to retrieve.

        Returns:
            EncryptionKeyView: The encryption key view object corresponding to the ID.
        """
        self.encryption_key_request_validator.validate_read_request(id)

        encryption_key: EncryptionKeyView = await self.get_record_by_id(id)

        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()

        # Decrypt the keys before returning them
        encryption_key.public_key = secure_encryptor.decrypt(encryption_key.public_key)
        encryption_key.private_key = secure_encryptor.decrypt(encryption_key.private_key)

        return encryption_key

    async def get_active_encryption_key_by_type(self, key_type: EncryptionKeyType) -> EncryptionKeyView:
        """
        Retrieve an active encryption key by its type.

        Args:
            key_type (EncryptionKeyType): The type of the key.

        Returns:
            EncryptionKeyView: The encryption key view object with the specified type.
        """
        self.encryption_key_request_validator.validate_key_type(key_type)

        repository = self.get_repository()
        encryption_key = await repository.get_active_encryption_key_by_type(key_type)

        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()

        # Decrypt the keys before returning them
        encryption_key.public_key = secure_encryptor.decrypt(encryption_key.public_key)
        encryption_key.private_key = secure_encryptor.decrypt(encryption_key.private_key)

        return encryption_key

    async def delete_disabled_encryption_key(self, id: int) -> EncryptionKeyView:
        """
        Delete an encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to delete.

        Returns:
            EncryptionKeyView: The deleted encryption key view object.
        """
        self.encryption_key_request_validator.validate_delete_request(id)

        repository = self.get_repository()
        existing_encryption_key: EncryptionKeyModel = await repository.get_encryption_key_by_id(
            id, EncryptionKeyStatus.DISABLED)

        updated_encryption_key_request = EncryptionKeyView.model_validate(existing_encryption_key)
        updated_encryption_key_request.key_status = EncryptionKeyStatus.DELETED

        result: EncryptionKeyView = await self.update_record(id, updated_encryption_key_request)

        response: EncryptionKeyView = EncryptionKeyView()
        response.id = result.id
        response.status = result.status
        response.create_time = result.create_time
        response.update_time = result.update_time
        response.key_type = result.key_type
        response.key_status = result.key_status

        return response

    async def disable_passive_encryption_key(self, id: int) -> EncryptionKeyView:
        """
        Disable passive encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to disable.

        Returns:
            EncryptionKeyView: The disabled encryption key view object.
        """
        self.encryption_key_request_validator.validate_disable_request(id)

        repository = self.get_repository()
        existing_encryption_key: EncryptionKeyModel = await repository.get_encryption_key_by_id(
            id, EncryptionKeyStatus.PASSIVE)

        updated_encryption_key_request = EncryptionKeyView.model_validate(existing_encryption_key)
        updated_encryption_key_request.key_status = EncryptionKeyStatus.DISABLED

        result: EncryptionKeyView = await self.update_record(id, updated_encryption_key_request)

        response: EncryptionKeyView = EncryptionKeyView()
        response.id = result.id
        response.status = result.status
        response.create_time = result.create_time
        response.update_time = result.update_time
        response.key_type = result.key_type
        response.key_status = result.key_status

        return response
