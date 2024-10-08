from abc import ABC, abstractmethod

from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse


class AsyncPAIGAuthorizer(ABC):

    @abstractmethod
    async def authorize(self, request: AuthzRequest) -> AuthzResponse:
        """
        Authorize the request.

        Args:
            request (AuthzRequest): The authorization request.

        Returns:
            AuthzResponse: The authorization response.
        """
        pass

    @abstractmethod
    async def authorize_vector_db(self, request: VectorDBAuthzRequest) -> VectorDBAuthzResponse:
        """
        Authorize the VectorDB request.

        Args:
            request (VectorDBAuthzRequest): The VectorDB authorization request.

        Returns:
            VectorDBAuthzResponse: The VectorDB authorization response.
        """
        pass
