import logging
from core.controllers.base_controller import BaseController
from api.apikey.database.db_models.paig_api_key_model import PaigApiKeyModel
from core.utils import SingletonDepends
from api.apikey.database.db_operations.paig_api_key_repository import PaigApiKeyRepository
from api.apikey.api_schemas.paig_api_key import PaigApiKeyView

from api.apikey.services.paig_level1_encryption_key_service import PaigLevel1EncryptionKeyService
from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService

from api.encryption.utils.secure_encryptor import SecureEncryptor
from api.apikey.database.db_models.base_model import ApiKeyStatus
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from api.governance.services.ai_app_service import AIAppService
from core.db_session.transactional import Transactional, Propagation
from core.utils import convert_token_expiry_to_epoch_time, validate_token_expiry_time, short_uuid, validate_id
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import get_error_message, ERROR_FIELD_INVALID
from api.apikey.utils.apikey_secure_encryptor import apikey_encrypt, mask_api_key, apikey_decrypt
from core.constants import DEFAULT_TENANT_ID
import base64

SEMI_COLON_SEPARATOR  = ";"
COLON_SEPARATOR = ":"

logger = logging.getLogger(__name__)


class PaigApiKeyService(BaseController[PaigApiKeyModel, PaigApiKeyView]):
    def __init__(
            self,
            ai_app_service: AIAppService = SingletonDepends(AIAppService),
            paig_api_key_repository: PaigApiKeyRepository = SingletonDepends(PaigApiKeyRepository),
            paig_level1_encryption_key_service: PaigLevel1EncryptionKeyService = SingletonDepends(
                PaigLevel1EncryptionKeyService),
            paig_level2_encryption_key_service: PaigLevel2EncryptionKeyService = SingletonDepends(
                PaigLevel2EncryptionKeyService),
            secure_encryptor_factory: SecureEncryptorFactory = SingletonDepends(SecureEncryptorFactory)
    ):
        super().__init__(
            paig_api_key_repository,
            PaigApiKeyModel,
            PaigApiKeyView
        )
        self.paig_level1_encryption_key_service = paig_level1_encryption_key_service
        self.paig_level2_encryption_key_service = paig_level2_encryption_key_service
        self.secure_encryptor_factory = secure_encryptor_factory
        self.ai_app_service = ai_app_service

    async def get_repository(self) -> PaigApiKeyRepository:
        return self.repository

    async def get_api_key_by_ids(self, key_ids: list):
        api_keys =  await self.repository.get_api_key_by_ids(key_ids)
        api_keys_list = []
        for api_key in api_keys:
            api_keys_list.append(api_key.to_ui_dict())
        return api_keys_list


    async def get_api_keys_by_application_id(self, *args):
        return await self.repository.get_api_keys_by_application_id(*args)

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_api_key(self, request):
        level1_encrypted_key = await self.paig_level1_encryption_key_service.get_active_paig_level1_encryption_key()
        level2_encrypted_key = await self.paig_level2_encryption_key_service.get_active_paig_level2_encryption_key()

        secure_encryptor: SecureEncryptor = await self.secure_encryptor_factory.get_or_create_secure_encryptor()

        try:
            level1_decrypted_key = secure_encryptor.decrypt(level1_encrypted_key.paig_key_value)
            level2_decrypted_key = secure_encryptor.decrypt(level2_encrypted_key.paig_key_value)
        except Exception as e:
            logger.error(f"Error decrypting encryption key: {e}")
            raise BadRequestException(f"Failed to create API key")

        api_key_uuid = short_uuid()

        token_expiry = request.get('token_expiry')
        token_expiry_epoch_time = convert_token_expiry_to_epoch_time(token_expiry)

        if not validate_token_expiry_time(token_expiry_epoch_time):
            raise BadRequestException(get_error_message(ERROR_FIELD_INVALID, "Expiry Date", token_expiry))

        shield_server_url = await self.ai_app_service.get_shield_server_url()

        user_id = request.get('user_id')
        tenant_id = DEFAULT_TENANT_ID
        scopes = request.get('scopes')
        scope = scopes[0] if scopes else "3"
        app_id = request.get('application_id')

        # validate user_id and app_id
        validate_id(user_id, "User ID")
        validate_id(app_id, "Application ID")

        user_data = f"{user_id}{COLON_SEPARATOR}{tenant_id}{COLON_SEPARATOR}{token_expiry_epoch_time}{COLON_SEPARATOR}{scope}{COLON_SEPARATOR}{app_id}"

        level1_encrypted_data = apikey_encrypt(user_data, level1_decrypted_key, "v2")


        level2_data = str(level1_encrypted_key.key_id) + COLON_SEPARATOR + level1_encrypted_data
        level2_encrypted_data = apikey_encrypt(level2_data, level2_decrypted_key, "v2")


        api_key_temp = str(api_key_uuid) + COLON_SEPARATOR + "2" + COLON_SEPARATOR + str(level2_encrypted_key.key_id) + COLON_SEPARATOR + level2_encrypted_data + SEMI_COLON_SEPARATOR + shield_server_url

        final_api_key = base64.urlsafe_b64encode(api_key_temp.encode()).decode('utf-8')
        masked_api_key = mask_api_key(final_api_key)

        request['api_key_encrypted'] = None
        request['api_key_masked'] = masked_api_key
        request['key_status'] = ApiKeyStatus.ACTIVE
        request['api_scope_id'] = request.get('scopes')[0] if request.get('scopes') else 3
        request['key_id'] = api_key_uuid

        # remove scopes from request
        request.pop('scopes', None)

        paig_app_api_key = await self.repository.create_api_key(request)
        paig_app_api_key_dict = paig_app_api_key.to_ui_dict()
        paig_app_api_key_dict['apiKeyMasked'] = final_api_key
        return paig_app_api_key_dict


    @Transactional(propagation=Propagation.REQUIRED)
    async def disable_api_key(self, key_id: int):
        paig_app_api_key =  await self.repository.disable_api_key(key_id)
        return paig_app_api_key.to_ui_dict()

    @Transactional(propagation=Propagation.REQUIRED)
    async def permanent_delete_api_key(self, key_id: int):
        return await self.repository.permanent_delete_api_key(key_id)


    async def get_paig_api_key_by_uuid(self, key_uuid: str):
        return await self.repository.get_paig_api_key_by_uuid(key_uuid)







