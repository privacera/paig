from typing import Tuple

from core.constants import DEFAULT_TENANT_ID
from core.utils import current_utc_time, SingletonDepends
from api.encryption.api_schemas.encryption_key import EncryptionKeyView
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType
from api.encryption.services.encryption_key_service import EncryptionKeyService
from api.governance.services.ai_app_service import AIAppService
from core.middlewares.usage import background_capture_event
from core.factory.events import DownloadAIApplicationConfigEvent


class AIAppConfigDownloadController:

    def __init__(self,
                 ai_app_service: AIAppService = SingletonDepends(AIAppService),
                 encryption_key_service: EncryptionKeyService = SingletonDepends(EncryptionKeyService)):
        self.ai_app_service = ai_app_service
        self.encryption_key_service = encryption_key_service

    async def get_ai_app_config_json_data(self, id: int) -> Tuple[str, dict]:
        """
        Get the configuration of an AI application in JSON format.

        Args:
            id (int): The ID of the AI application.

        Returns:
            Tuple[str, dict]: A tuple containing the name of the AI application and its configuration in JSON format.
        """
        ai_application = await self.ai_app_service.get_ai_application_by_id(id)
        shield_server_key: EncryptionKeyView = await self.encryption_key_service.get_active_encryption_key_by_type(EncryptionKeyType.MSG_PROTECT_SHIELD)
        shield_plugin_key: EncryptionKeyView = await self.encryption_key_service.get_active_encryption_key_by_type(EncryptionKeyType.MSG_PROTECT_PLUGIN)
        shield_server_url = await self.ai_app_service.get_shield_server_url()
        await background_capture_event(event=DownloadAIApplicationConfigEvent())
        # Simulating retrieval of data from a database or other source
        return ai_application.name, {
            "applicationId": ai_application.id,
            "applicationKey": ai_application.application_key,
            "tenantId": DEFAULT_TENANT_ID,
            "apiServerUrl": "",
            "apiKey": "none",
            "shieldServerUrl": shield_server_url,
            "shieldServerKeyId": shield_server_key.id,
            "shieldServerPublicKey": shield_server_key.public_key,
            "shieldPluginKeyId": shield_plugin_key.id,
            "shieldPluginPrivateKey": shield_plugin_key.private_key,
            "dateOfDownload": str(current_utc_time().astimezone())
        }
