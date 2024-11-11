from fastapi import APIRouter, Request, Depends

from api.shield.controllers.shield_controller import ShieldController
from core.utils import SingletonDepends

init_app_router = APIRouter()

shield_controller_instance = Depends(SingletonDepends(ShieldController, called_inside_fastapi_depends=True))


@init_app_router.post("")
async def init_app(request: Request, shield_controller: ShieldController = shield_controller_instance):
    """
    Handles POST requests to initialize an application.

    This endpoint processes a request to initialize the application and delegates
    the task to the `ShieldController` to perform the initialization logic.

    Returns:
        The result of the application initialization operation handled by `ShieldController`.
    """
    return await shield_controller.init_app(request)
