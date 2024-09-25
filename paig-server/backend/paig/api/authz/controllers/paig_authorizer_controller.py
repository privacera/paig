
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from api.authz.services.paig_authorizer_service import PAIGAuthorizerService
from core.utils import SingletonDepends


class PAIGAuthorizerController:
    """
    Controller class for handling PAIG authorization requests.

    Args:
        paig_authorizer_service (PAIGAuthorizerService): The service handling PAIG authorization operations.
    """

    def __init__(self, paig_authorizer_service: PAIGAuthorizerService = SingletonDepends(PAIGAuthorizerService)):
        self.paig_authorizer_service = paig_authorizer_service

    async def authorize(self, request: AuthzRequest) -> AuthzResponse:
        """
        Authorize a request.

        Args:
            request (AuthzRequest): The request to authorize.

        Returns:
            AuthzResponse: The response to the authorization request.
        """
        return await self.paig_authorizer_service.authorize(request)

    async def authorize_vector_db(self, request: VectorDBAuthzRequest) -> VectorDBAuthzResponse:
        """
        Authorize a request to access a vector database.

        Args:
            request (VectorDBAuthzRequest): The request to authorize.

        Returns:
            VectorDBAuthzResponse: The response to the authorization request.
        """
        return await self.paig_authorizer_service.authorize_vector_db(request)