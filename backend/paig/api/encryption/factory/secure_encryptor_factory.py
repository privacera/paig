from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel
from api.encryption.database.db_operations.encryption_master_key_repository import EncryptionMasterKeyRepository
from api.encryption.utils.secure_encryptor import SecureEncryptor
from core.utils import SingletonDepends


class SecureEncryptorFactory:

    def __init__(self, encryption_master_key_repository: EncryptionMasterKeyRepository = SingletonDepends(EncryptionMasterKeyRepository)):
        self.encryption_master_key_repository = encryption_master_key_repository
        self.secure_encryptor : SecureEncryptor | None = None

    # noinspection PyMethodMayBeStatic
    async def get_or_create_secure_encryptor(self) -> SecureEncryptor:
        """
        Get a secure encryptor

        Args: encryption_master_key_repository (EncryptionMasterKeyRepository): The repository handling encryption
        master key database operations.

        Returns:
            SecureEncryptor: The secure encryptor instance.
        """
        if self.secure_encryptor is None:
            master_key: EncryptionMasterKeyModel = await self.encryption_master_key_repository.get_active_encryption_master_key()
            self.secure_encryptor = SecureEncryptor(master_key.key)
        return self.secure_encryptor