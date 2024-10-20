from api.governance.database.db_operations.ai_app_apikey_repository import AIAppAPIKeyRepository, \
    AIAppEncryptionKeyRepository
from core.utils import SingletonDepends, generate_expiry_epoch, epoch_to_datetime
from core.utils import get_key_from_hex, generate_hex_key
from api.governance.database.db_models.ai_app_apikey_model import AIApplicationEncryptionKeyModel, AIApplicationAPIKeyModel
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import logging

logger = logging.getLogger(__name__)


def generate_plain_api_key():
    expiry = generate_expiry_epoch(30)
    scope = 1
    key = str(expiry) + ":" + str(scope)
    return key, expiry


class AIAppAPIKeyService:
    def __init__(self, ai_app_apikey_repository: AIAppAPIKeyRepository = SingletonDepends(AIAppAPIKeyRepository),
                 ai_app_encryptionkey_repository: AIAppEncryptionKeyRepository = SingletonDepends(
                     AIAppEncryptionKeyRepository)
                 ):
       self.ai_app_apikey_repository = ai_app_apikey_repository
       self.ai_app_encryptionkey_repository = ai_app_encryptionkey_repository

    @staticmethod
    def encrypt_api_key(api_key: str, master_key: bytes) -> bytes:
        # Generate a random initialization vector (IV)
        iv = os.urandom(16)

        # Create AES cipher using the master key and IV
        cipher = Cipher(algorithms.AES(master_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt the API key
        encrypted_api_key = encryptor.update(api_key.encode()) + encryptor.finalize()

        # Return both the IV and encrypted API key
        return iv + encrypted_api_key

    @staticmethod
    def decrypt_api_key(encrypted_api_key: bytes, master_key: bytes) -> str:
        # Split the IV and the actual encrypted API key
        iv = encrypted_api_key[:16]  # First 16 bytes are the IV
        actual_encrypted_key = encrypted_api_key[16:]  # Rest is the encrypted key

        # Create AES cipher using the master key and IV
        cipher = Cipher(algorithms.AES(master_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()

        # Decrypt the API key
        decrypted_api_key = decryptor.update(actual_encrypted_key) + decryptor.finalize()

        return decrypted_api_key.decode()

    async def create_app_encryption_key(self, app_id):
        key = generate_hex_key()
        new_record = AIApplicationEncryptionKeyModel(application_id=app_id, key=key)
        return await self.ai_app_encryptionkey_repository.create_encryption_key(new_record)

    async def generate_api_key(self, app_id, shield_server_url):
        # Get All active encryption keys
        encryption_keys = await self.ai_app_encryptionkey_repository.get_valid_encryption_keys(app_id)
        if not encryption_keys:
            logger.info("No encryption keys found for the application. Creating a new encryption key.")
            encryption_key = await self.create_app_encryption_key(app_id)
            encryption_keys = [encryption_key]

        if not encryption_keys or len(encryption_keys) == 0:
            logger.error("No encryption keys found for the application. Failed to create a new encryption key.")
            raise Exception("Failed to create api key")
        # Get the latest encryption key
        encryption_key = encryption_keys[0]
        encryption_key = get_key_from_hex(encryption_key.key)

        # Generate API Key
        plain_key, expiry = generate_plain_api_key()

        # Encrypt API Key
        encrypted_api_key = self.encrypt_api_key(plain_key, encryption_key)
        encrypted_api_key = encrypted_api_key.hex()
        # Add additional information to the API Key
        encrypted_api_key = encrypted_api_key + ":" + str(app_id) + ":" + str(shield_server_url)

        # encode the api key
        encrypted_api_key = base64.b64encode(encrypted_api_key.encode('utf-8')).decode('utf-8')

        # Insert the API Key into the database
        expiry = epoch_to_datetime(expiry)

        # Mask the API Key before storing
        api_key_masked = 'X' * (len(encrypted_api_key) - 6) + encrypted_api_key[-6:]

        model = AIApplicationAPIKeyModel(
            application_id=app_id,
            api_key=api_key_masked,
            scope=1,
            expiry_time=expiry
        )
        await self.ai_app_apikey_repository.create_api_key(model)

        return {"apiKey": encrypted_api_key, "expiry": expiry}

    async def validate_api_key(self, api_key: str):
        # Decode the API Key
        decoded_key = (base64.b64decode(api_key.encode('utf-8'))).decode('utf-8')

        # Split the API Key into its components
        key_components = decoded_key.split(":")
        if len(key_components) < 3:
            raise Exception("Invalid API Key")
        encrypted_key = key_components[0]
        app_id = key_components[1]

        # validate the app_id
        try:
            app_id = int(app_id)
        except Exception as e:
            raise Exception("Invalid API Key")

        # Get the encryption key for the application
        encryption_master_key = await self.ai_app_encryptionkey_repository.get_valid_encryption_keys(app_id)
        if not encryption_master_key:
            raise Exception("Invalid API Key")
        # Decrypt the API Key with all possible encryption keys
        decrypted_key = None
        for key in encryption_master_key:
            master_key = get_key_from_hex(key.key)
            try:
                decrypted_key = self.decrypt_api_key(bytes.fromhex(encrypted_key), master_key)
                if decrypted_key:
                    break
            except Exception as e:
                continue

        # Invalidated if no key is decrypted
        if not decrypted_key:
            raise Exception("Invalid API Key")

        # check if the key is expired
        try:
            expiry = int(decrypted_key.split(":")[0])
            if expiry < generate_expiry_epoch(0):
                raise Exception("API Key expired")
        except Exception as e:
            logger.error("Error while validating API Key: %s", e)
            raise Exception("Invalid API Key")

        return app_id

