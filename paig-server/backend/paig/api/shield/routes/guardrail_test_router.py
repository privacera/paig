from fastapi import APIRouter, Header, Body, Depends
from typing import Annotated, Optional

from api.shield.controllers.shield_controller import ShieldController
from core.utils import SingletonDepends
guardrail_test_router = APIRouter()

shield_controller_instance = Depends(SingletonDepends(ShieldController, called_inside_fastapi_depends=True))


@guardrail_test_router.post("")
async def guardrail_test(request: Annotated[dict | None, Body()],
                         x_tenant_id: Annotated[Optional[str], Header()] = None,
                         x_user_role: Annotated[Optional[str], Header()] = None,
                         shield_controller: ShieldController = shield_controller_instance):
    """
    Handles POST requests to initialize an application.

    This endpoint processes a request to initialize the application and delegates
    the task to the `ShieldController` to perform the initialization logic.

    Returns:
        The result of the application initialization operation handled by `ShieldController`.
    """
    return await shield_controller.guardrail_test(request, tenant_id=x_tenant_id, user_role=x_user_role)