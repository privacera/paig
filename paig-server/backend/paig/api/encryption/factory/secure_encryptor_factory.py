from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel
from api.encryption.database.db_operations.encryption_master_key_repository import EncryptionMasterKeyRepository
from api.encryption.utils.secure_encryptor import SecureEncryptor
from core.utils import SingletonDepends
from typing import Optional



class SecureEncryptorFactory:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, encryption_master_key_repository: EncryptionMasterKeyRepository = SingletonDepends(EncryptionMasterKeyRepository)):
        if self._initialized:
            return
        self.encryption_master_key_repository = encryption_master_key_repository
        self.secure_encryptor: Optional[SecureEncryptor] = None
        self._initialized = True

    async def get_or_create_secure_encryptor(self) -> SecureEncryptor:
        """
        Lazily initialize and return a SecureEncryptor instance.

        Returns:
            SecureEncryptor: The secure encryptor instance.
        """
        if self.secure_encryptor is None:
            master_key: EncryptionMasterKeyModel = await self.encryption_master_key_repository.get_active_encryption_master_key()
            self.secure_encryptor = SecureEncryptor(master_key.key)
        return self.secure_encryptor
