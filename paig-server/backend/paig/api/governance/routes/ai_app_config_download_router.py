import json
from io import BytesIO

from fastapi import Depends, APIRouter
from starlette.responses import StreamingResponse

from api.governance.controllers.ai_app_config_download_controller import AIAppConfigDownloadController
from core.utils import SingletonDepends

ai_app_config_download_router = APIRouter()

ai_app_config_download_controller_instance = Depends(SingletonDepends(AIAppConfigDownloadController, called_inside_fastapi_depends=True))


@ai_app_config_download_router.get("/config/json/download")
async def download_json(
        id: int,
        ai_app_config_download_controller: AIAppConfigDownloadController = ai_app_config_download_controller_instance
):
    """
    Download the configuration of an AI application in JSON format.

    Args:
        id (int): The ID of the AI application.
        ai_app_config_download_controller (AIAppConfigDownloadController): The controller class for handling AI application configuration download operations

    Returns:
        StreamingResponse: The JSON data of the AI application configuration.
    """
    ai_app, ai_app_json_data = await ai_app_config_download_controller.get_ai_app_config_json_data(id)
    # Convert the data to a JSON string
    json_data = json.dumps(ai_app_json_data, indent=2)

    # Replace spaces with hyphens in the AI application name
    ai_app = ai_app.strip().replace(" ", "-")

    # Create a BytesIO buffer and write the JSON data to it
    buffer = BytesIO()
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="application/json", headers={"Content-Disposition": f"attachment;filename=privacera-shield-{ai_app}-config.json"})
