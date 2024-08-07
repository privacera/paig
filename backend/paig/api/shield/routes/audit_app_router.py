from fastapi import APIRouter, Body, Depends
from typing import Annotated
from api.shield.controllers.shield_controller import ShieldController
from core.utils import SingletonDepends

audit_app_router = APIRouter()

shield_controller_instance = Depends(SingletonDepends(ShieldController, called_inside_fastapi_depends=True))


@audit_app_router.post("")
async def audit(request: Annotated[dict | None, Body()],
                shield_controller: ShieldController = shield_controller_instance):
    """
       Handles POST requests to audit logs.

       This endpoint processes an audit request and delegates the task to the `ShieldController`
       to handle the audit logic.

       Returns:
           The result of the audit operation handled by `ShieldController`.
       """
    return await shield_controller.audit(request)
