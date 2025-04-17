from fastapi import Request
import base64
import logging
from core.utils import SingletonDepends
from api.apikey.services.paig_level1_encryption_key_service import PaigLevel1EncryptionKeyService
from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService
from api.apikey.services.paig_api_key_service import PaigApiKeyService
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from core.exceptions import BadRequestException
from api.apikey.factory.apikey_secure_encryptor import apikey_decrypt
from api.apikey.utils import validate_token_expiry_time
from api.encryption.utils.secure_encryptor import SecureEncryptor
from core.config import load_config_file

logger = logging.getLogger(__name__)

conf = load_config_file()


class APIKeyValidator:
    def __init__(
            self,
            paig_api_key_service: PaigApiKeyService = SingletonDepends(PaigApiKeyService),
            secure_encryptor_factory: SecureEncryptorFactory = SingletonDepends(SecureEncryptorFactory),
            paig_level1_encryption_key_service: PaigLevel1EncryptionKeyService = SingletonDepends(
                PaigLevel1EncryptionKeyService),
            paig_level2_encryption_key_service: PaigLevel2EncryptionKeyService = SingletonDepends(
                PaigLevel2EncryptionKeyService)
    ):
        self.paig_api_key_service = paig_api_key_service
        self.secure_encryptor_factory = secure_encryptor_factory
        self.paig_level1_encryption_key_service = paig_level1_encryption_key_service
        self.paig_level2_encryption_key_service= paig_level2_encryption_key_service

    async def validate_api_key(self, request: Request):
        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()
        api_key_config = conf.get("api_key")
        api_key_header_name = api_key_config.get("header_name")
        paig_app_api_key = request.headers.get(api_key_header_name)

        if not paig_app_api_key:
            logger.error("API key header is missing")
            raise BadRequestException("API key header is missing")

        try:
            decode_final_api_key = base64.urlsafe_b64decode(paig_app_api_key.encode()).decode('utf-8')
        except Exception as e:
            logger.error("Invalid API key", exc_info=e)
            raise BadRequestException("Invalid API key")

        split_api_key_with_semi_colon = decode_final_api_key.split(";")
        if len(split_api_key_with_semi_colon) != 2:
            raise BadRequestException("Invalid API key")

        split_decode_final_api_key = split_api_key_with_semi_colon[0].split(":")
        if len(split_decode_final_api_key) != 4:
            raise BadRequestException("Invalid API key")

        api_key_uuid = split_decode_final_api_key[0]
        level2_uuid = split_decode_final_api_key[2]
        level2_encrypted_data = split_decode_final_api_key[3]

        api_key = await self.paig_api_key_service.get_paig_api_key_by_uuid(api_key_uuid)
        if not api_key:
            raise BadRequestException("API Key has expired")

        level2_encrypted_key = await self.paig_level2_encryption_key_service.get_paig_level2_encryption_key_by_uuid(
            level2_uuid)
        if not level2_encrypted_key:
            raise BadRequestException("Invalid API key")
        try:
            level2_key_value = secure_encryptor.decrypt(level2_encrypted_key.paig_key_value)
            decryptedData2 = apikey_decrypt(level2_encrypted_data, level2_key_value, "v2")
        except Exception as e:
            logger.error("Invalid API key", exc_info=e)
            raise BadRequestException("Invalid API key")



        split_decryptedData2 = decryptedData2.split(":")
        if len(split_decryptedData2) != 2:
            raise BadRequestException("Invalid API key")

        level1_uuid = split_decryptedData2[0]
        level1_encrypted_data = split_decryptedData2[1]

        level1_encrypted_key = await self.paig_level1_encryption_key_service.get_paig_level1_encryption_key_by_uuid(
            level1_uuid)
        if not level1_encrypted_key:
            raise BadRequestException("Invalid API key")

        try:
            level1_key_value = secure_encryptor.decrypt(level1_encrypted_key.paig_key_value)
            decryptedData1 = apikey_decrypt(level1_encrypted_data, level1_key_value, "v2")
        except Exception as e:
            logger.error("Invalid API key", exc_info=e)
            raise BadRequestException("Invalid API key")


        split_decryptedData1 = decryptedData1.split(":")

        if len(split_decryptedData1) != 5:
            raise BadRequestException("Invalid API key")

        user_id = int(split_decryptedData1[0])
        token_expiry_epoch_time = split_decryptedData1[2]
        api_id = int(split_decryptedData1[4])

        if not validate_token_expiry_time(int(token_expiry_epoch_time)):
            raise BadRequestException("API Key is expired")

        return {
            "user_id": user_id,
            "api_id": api_id
        }
