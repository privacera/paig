from core.factory.database_initiator import BaseOperations
from sqlalchemy.exc import NoResultFound
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from api.apikey.database.db_models.paig_level2_encryption_key_model import PaigLevel2EncryptionKeyModel
from api.apikey.utils import EncryptionKeyStatus


class PaigLevel2EncryptionKeyRepository(BaseOperations[PaigLevel2EncryptionKeyModel]):
    """
        Repository class for handling database operations related to encryption key models.

        Inherits from BaseOperations[PaigLevel2EncryptionKeyModel], providing generic CRUD operations.

        This class inherits all methods from BaseOperations[PaigLevel2EncryptionKeyModel].
        """

    def __init__(self):
        """
        Initialize the PaigLevel2EncryptionKeyRepository.
        """
        super().__init__(PaigLevel2EncryptionKeyModel)

    async def get_active_paig_level2_encryption_key(self) -> PaigLevel2EncryptionKeyModel:
        """
        Retrieve an active encryption key.

        Returns:
            PaigLevel2EncryptionKeyModel: The active encryption key.

        Raises:
            NoResultFound: If no active encryption key is found.
        """
        try:
            return await self.get_by(filters={"key_status": EncryptionKeyStatus.ACTIVE.value}, unique=True)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Active Level2 Encryption key", "key_status", EncryptionKeyStatus.ACTIVE.value))

    async def get_paig_level2_encryption_key_by_id(self, key_id: int) -> PaigLevel2EncryptionKeyModel:
        """
        Retrieve an encryption key by its ID.

        Args:
            key_id (int): The ID of the key.

        Returns:
            PaigLevel2EncryptionKeyModel: The encryption key with the specified ID.

        Raises:
            NoResultFound: If no encryption key with the specified ID is found.
        """
        try:
            return await self.get_by(filters={"id": key_id}, unique=True)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Level2 Encryption key", "keyId", key_id))

    async def get_paig_level2_encryption_key_by_uuid(self, key_uuid: str) -> PaigLevel2EncryptionKeyModel:
        """
        Retrieve an encryption key by its UUID.

        Args:
            key_uuid (str): The UUID of the key.

        Returns:
            PaigLevel2EncryptionKeyModel: The encryption key with the specified UUID.

        Raises:
            NoResultFound: If no encryption key with the specified UUID is found.
        """
        try:
            return await self.get_by(filters={"key_id": key_uuid}, unique=True)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Level2 Encryption key", "keyUuid", key_uuid))