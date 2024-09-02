from sqlalchemy.exc import NoResultFound
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.factory.database_initiator import BaseOperations
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyModel, EncryptionKeyType, \
    EncryptionKeyStatus


class EncryptionKeyRepository(BaseOperations[EncryptionKeyModel]):
    """
    Repository class for handling database operations related to encryption key models.

    Inherits from BaseOperations[EncryptionKey], providing generic CRUD operations.

    This class inherits all methods from BaseOperations[EncryptionKey].
    """

    def __init__(self):
        """
        Initialize the AIAppRepository.

        Args:
            db_session (Session): The database session to use for operations.
        """
        super().__init__(EncryptionKeyModel)

    async def get_active_encryption_key_by_type(self, key_type: EncryptionKeyType) -> EncryptionKeyModel:
        """
        Retrieve an active encryption key by its type.

        Args:
            key_type (EncryptionKeyType): The type of the key.

        Returns:
            EncryptionKeyModel: The encryption key with the specified type.

        Raises:
            NoResultFound: If no encryption key with the specified type is found.
        """
        try:
            return await self.get_by(filters={"key_type": key_type, "key_status": EncryptionKeyStatus.ACTIVE},
                                     unique=True)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "Active encryption key", "key_type",
                                                      key_type.value))

    async def get_encryption_key_by_id(self, key_id: int, key_status: EncryptionKeyStatus) -> EncryptionKeyModel:
        """
        Retrieve a passive encryption key by its ID.

        Args:
            key_id (int): The ID of the key.
            key_status (EncryptionKeyStatus): The status of the key.

        Returns:
            EncryptionKeyModel: The encryption key with the specified ID.

        Raises:
            NoResultFound: If no encryption key with the specified ID is found.
        """
        try:
            return await self.get_by(filters={"id": key_id, "key_status": key_status}, unique=True)
        except NoResultFound:
            raise NotFoundException(get_error_message(ERROR_RESOURCE_NOT_FOUND, "{} encryption key".format(key_status.value),
                                                      "ID", key_id))
