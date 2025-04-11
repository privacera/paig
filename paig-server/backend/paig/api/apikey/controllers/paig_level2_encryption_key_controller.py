from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND



class PaigLevel2EncryptionKeyController:
    """
    Controller class for handling level 2 encryption key operations.

    This class contains methods for interacting with the PaigLevel2EncryptionKeyService.
    """

    def __init__(self):
        """
        Initialize the PaigLevel2EncryptionKeyController.
        """
        self._level2_encryption_key_service = PaigLevel2EncryptionKeyService()

    async def get_paig_level2_encryption_key_by_id(self, key_id: str):
        """
        Retrieve a level 2 encryption key by its ID.

        Args:
            key_id (str): The ID of the level 2 encryption key to retrieve.
        """
        try:
            return await self._level2_encryption_key_service.get_paig_level2_encryption_key_by_id(key_id)
        except NotFoundException:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Level 2 encryption key", "keyId", key_id))

    async def create_paig_level2_encryption_key(self):
        """
        Create a new level 2 encryption key.
        """
        return await self._level2_encryption_key_service.create_paig_level2_encryption_key()
