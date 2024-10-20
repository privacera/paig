from api.governance.services.ai_app_apikey_service import AIAppAPIKeyService
from api.governance.services.ai_app_service import AIAppService
from core.utils import SingletonDepends
from core.db_session import Transactional, Propagation



class AIAppAPIKeyController:

    def __init__(self,
                 ai_app_apikey_service:  AIAppAPIKeyService = SingletonDepends(AIAppAPIKeyService),
                 ai_app_service: AIAppService = SingletonDepends(AIAppService),
                 ):
        self.ai_app_apikey_service = ai_app_apikey_service
        self.ai_app_service = ai_app_service

    @Transactional(propagation=Propagation.REQUIRED)
    async def generate_api_key(self, app_id: int):
        shield_server_url = await self.ai_app_service.get_shield_server_url()
        return await self.ai_app_apikey_service.generate_api_key(app_id, shield_server_url)

    async def validate_api_key(self, api_key: str):
        app_id =  await self.ai_app_apikey_service.validate_api_key(api_key)
        if app_id:
            return {"message": "API key is valid", "app_id": app_id}
        else:
            return {"message": "API key is invalid"}