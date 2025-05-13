from api.encryption.utils.secure_encryptor import SecureEncryptor
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from core.utils import SingletonDepends

class CryptoService:

    def __init__(self):
        self.secure_encryptor_factory: SecureEncryptorFactory = SingletonDepends(SecureEncryptorFactory)

    async def encrypt(self, data: str):
        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()
        return secure_encryptor.encrypt(data)

    async def decrypt(self, token: str):
        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()
        return secure_encryptor.decrypt(token)