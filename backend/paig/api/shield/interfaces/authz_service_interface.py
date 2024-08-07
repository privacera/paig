from abc import ABC, abstractmethod

from api.shield.model.authz_service_request import AuthzServiceRequest
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest


class IAuthzClient(ABC):
    """
    An abstract base class for authorization service clients.

    Methods:
        post_authorize(authz_service_request: AuthzServiceRequest, tenant_id):
            An abstract method for sending an authorization request.

        post_authorize_vectordb(authz_service_request: AuthorizeVectorDBRequest, tenant_id):
            An abstract method for sending a VectorDB authorization request.
    """

    @abstractmethod
    def post_authorize(self, authz_service_request: AuthzServiceRequest, tenant_id):
        """
        Sends an authorization request.

        Args:
            authz_service_request (AuthzServiceRequest): The authorization request.
            tenant_id: The tenant id.

        This is an abstract method and must be implemented in a subclass.
        """
        pass

    @abstractmethod
    def post_authorize_vectordb(self, authz_service_request: AuthorizeVectorDBRequest, tenant_id):
        """
        Sends a VectorDB authorization request.

        Args:
            authz_service_request (AuthorizeVectorDBRequest): The VectorDB authorization request.
            tenant_id: The tenant id.

        This is an abstract method and must be implemented in a subclass.
        """
        pass
