from typing import List
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_ENCRYPTION_MASTER_KEY_NOT_FOUND
from core.factory.database_initiator import BaseOperations
from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel


class EncryptionMasterKeyRepository(BaseOperations[EncryptionMasterKeyModel]):
    """
    Repository class for handling database operations related to encryption master key models.

    Inherits from BaseOperations[EncryptionMasterKeyModel], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[EncryptionMasterKeyModel].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EncryptionMasterKeyModel)

    async def get_active_encryption_master_key(self) -> EncryptionMasterKeyModel:
        """
        Retrieve an active encryption master key.

        Returns:
            EncryptionMasterKeyModel: The encryption master key with the specified type.

        Raises:
            NoResultFound: If no encryption master key with the specified type is found.
        """
        # Get only 1 record with ascending by create_time
        keys: List[EncryptionMasterKeyModel] = await self.get_all(order_by="create_time,asc", limit=1)
        if not keys:
            raise NotFoundException(get_error_message(ERROR_ENCRYPTION_MASTER_KEY_NOT_FOUND))
        return keys[0]
