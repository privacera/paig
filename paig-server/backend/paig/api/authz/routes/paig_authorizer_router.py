from fastapi import APIRouter, Depends

from api.authz.authorizer.paig_authorizer import AuthzRequest, AuthzResponse, VectorDBAuthzRequest, VectorDBAuthzResponse
from api.authz.controllers.paig_authorizer_controller import PAIGAuthorizerController
from core.utils import SingletonDepends

paig_authorizer_router = APIRouter()

paig_authorizer_controller_instance: PAIGAuthorizerController = Depends(SingletonDepends(PAIGAuthorizerController, called_inside_fastapi_depends=True))


@paig_authorizer_router.post("")
async def authorize(
        authz_request: AuthzRequest,
        paig_authorizer_controller: PAIGAuthorizerController = paig_authorizer_controller_instance
) -> AuthzResponse:
    """
    Authorize the provided request.
    """
    return await paig_authorizer_controller.authorize(authz_request)


@paig_authorizer_router.post("/vectordb")
async def authorize(
        authz_request: VectorDBAuthzRequest,
        paig_authorizer_controller: PAIGAuthorizerController = paig_authorizer_controller_instance
) -> VectorDBAuthzResponse:
    """
    Get vector db filter expression for the provided request.
    """
    return await paig_authorizer_controller.authorize_vector_db(authz_request)
