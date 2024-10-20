from fastapi import APIRouter, Depends

from api.governance.controllers.ai_app_apikey_controller import AIAppAPIKeyController
from core.utils import SingletonDepends

ai_app_apikey_router = APIRouter()

ai_app_apikey_controller_instance = Depends(SingletonDepends(AIAppAPIKeyController, called_inside_fastapi_depends=True))


@ai_app_apikey_router.post("/generate")
async def generate_api_key(
        app_id: int,
        ai_app_apikey_controller: AIAppAPIKeyController = ai_app_apikey_controller_instance
):
    """
    Generated Application API Key
    """
    return await ai_app_apikey_controller.generate_api_key(app_id)


@ai_app_apikey_router.post("/validate")
async def validate_api_key(
        api_key: str,
        ai_app_apikey_controller: AIAppAPIKeyController = ai_app_apikey_controller_instance
):
    """
    Generated Application API Key
    """
    return await ai_app_apikey_controller.validate_api_key(api_key)