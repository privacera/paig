from fastapi import APIRouter, Header, Body, Depends
from typing import Annotated, Optional
from api.shield.controllers.shield_controller import ShieldController
from core.utils import SingletonDepends

authorize_vectordb_router = APIRouter()

shield_controller_instance = Depends(SingletonDepends(ShieldController, called_inside_fastapi_depends=True))


@authorize_vectordb_router.post("")
async def authorize_vectordb_app(request: Annotated[dict | None, Body()],
                                 x_tenant_id: Annotated[Optional[str], Header()] = None,
                                 x_user_role: Annotated[Optional[str], Header()] = None,
                                 shield_controller: ShieldController = shield_controller_instance):
    """
    Handles POST requests to authorize access to VectorDB.

    This endpoint processes an authorization request specific to VectorDB access and
    delegates the task to the `ShieldController` to handle the authorization logic.

    Returns:
        The result of the VectorDB authorization operation handled by `ShieldController`.
    """
    return await shield_controller.authorize_vectordb(request, x_tenant_id, x_user_role)
