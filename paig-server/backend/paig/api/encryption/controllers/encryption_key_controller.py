from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.encryption.api_schemas.encryption_key import EncryptionKeyFilter, EncryptionKeyView
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType, EncryptionKeyStatus
from api.encryption.services.encryption_key_service import EncryptionKeyService
from core.utils import SingletonDepends


class EncryptionKeyController:
    """
    Controller class specifically for handling encryption key entities.

    Args:
        encryption_key_service (EncryptionKeyService): The service class for handling encryption key entities.
    """

    def __init__(self, encryption_key_service: EncryptionKeyService = SingletonDepends(EncryptionKeyService)):
        self.encryption_key_service = encryption_key_service

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
        if not filter.key_status or filter.key_status == "":
            filter.key_status = EncryptionKeyStatus.ACTIVE.value + "," + EncryptionKeyStatus.PASSIVE.value
        return await self.encryption_key_service.list_encryption_keys(filter, page_number, size, sort)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_encryption_key(self, key_type: EncryptionKeyType = EncryptionKeyType.MSG_PROTECT_SHIELD) -> (
            EncryptionKeyView):
        """
        Create a new encryption key.

        Args:
            key_type (EncryptionKeyType): The type of the key to create.

        Returns:
            EncryptionKeyView: The created encryption key view object.
        """
        return await self.encryption_key_service.create_encryption_key(key_type)

    async def get_public_encryption_key_by_id(self, id: int) -> EncryptionKeyView:
        """
        Retrieve the public encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to retrieve.

        Returns:
            str: The public encryption key corresponding to the ID.
        """
        return await self.encryption_key_service.get_public_encryption_key_by_id(id)

    async def get_encryption_key_by_id(self, id: int) -> EncryptionKeyView:
        """
        Retrieve an encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to retrieve.

        Returns:
            EncryptionKeyView: The encryption key view object corresponding to the ID.
        """
        return await self.encryption_key_service.get_encryption_key_by_id(id)

    async def get_active_encryption_key_by_type(self, key_type: EncryptionKeyType) -> EncryptionKeyView:
        """
        Retrieve an active encryption key by its type.

        Args:
            key_type (EncryptionKeyType): The type of the key.

        Returns:
            EncryptionKeyView: The encryption key view object with the specified type.
        """
        return await self.encryption_key_service.get_active_encryption_key_by_type(key_type)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_disabled_encryption_key(self, id: int):
        """
        Delete an encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to delete.
        """
        return await self.encryption_key_service.delete_disabled_encryption_key(id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def disable_passive_encryption_key(self, id: int):
        """
        Disable passive encryption key by its ID.

        Args:
            id (int): The ID of the encryption key to disable.
        """
        return await self.encryption_key_service.disable_passive_encryption_key(id)
