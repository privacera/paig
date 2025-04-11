from api.apikey.services.paig_level1_encryption_key_service import PaigLevel1EncryptionKeyService
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND



class PaigLevel1EncryptionKeyController:
    """
    Controller class for handling level 1 encryption key operations.

    This class contains methods for interacting with the PaigLevel1EncryptionKeyService.
    """

    def __init__(self):
        """
        Initialize the PaigLevel1EncryptionKeyController.
        """
        self._level1_encryption_key_service = PaigLevel1EncryptionKeyService()

    async def get_paig_level1_encryption_key_by_id(self, key_id: str):
        """
        Retrieve a level 1 encryption key by its ID.

        Args:
            key_id (str): The ID of the level 1 encryption key to retrieve.
        """
        try:
            return await self._level1_encryption_key_service.get_paig_level1_encryption_key_by_id(key_id)
        except NotFoundException:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Level 1 encryption key", "keyId", key_id))

    async def create_paig_level1_encryption_key(self):
        """
        Create a new level 1 encryption key.
        """
        return await self._level1_encryption_key_service.create_paig_level1_encryption_key()
