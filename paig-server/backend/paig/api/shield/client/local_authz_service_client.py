import logging
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from api.authz.services.paig_authorizer_service import PAIGAuthorizerService
from api.shield.interfaces.authz_service_interface import IAuthzClient
from api.shield.model.authz_service_request import AuthzServiceRequest
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.vectordb_authz_response import AuthorizeVectorDBResponse
from core.utils import SingletonDepends

logger = logging.getLogger(__name__)


class LocalAuthzClient(IAuthzClient):
    """
    A local client for the Authorization Service.

    Attributes:
        paig_authorizer (PAIGAuthorizer): An instance of PAIGAuthorizer.

    Methods:
        post_authorize(authz_service_request: AuthzServiceRequest, tenant_id) -> AuthzServiceResponse:
            Sends an authorization request and returns the response.

        post_authorize_vectordb(vectordb_auth_req: AuthorizeVectorDBRequest, tenant_id):
            Sends a VectorDB authorization request and returns the response.

        transform_authz_request(authz_service_request: AuthzServiceRequest) -> AuthzRequest:
            Transforms an AuthzServiceRequest into an AuthzRequest.

        transform_authz_response(authz_response: AuthzResponse) -> AuthzServiceResponse:
            Transforms an AuthzResponse into an AuthzServiceResponse.

        transform_vector_db_authz_request(vectordb_auth_req: AuthorizeVectorDBRequest) -> VectorDBAuthzRequest:
            Transforms an AuthorizeVectorDBRequest into a VectorDBAuthzRequest.

        transform_vector_db_authz_response(vectordb_response: VectorDBAuthzResponse) -> AuthorizeVectorDBResponse:
            Transforms a VectorDBAuthzResponse into an AuthorizeVectorDBResponse.
    """

    def __init__(self, paig_authorizer: PAIGAuthorizerService = SingletonDepends(PAIGAuthorizerService)):
        """
        Constructs a new LocalAuthzClient.

        Args:
            paig_authorizer (PAIGAuthorizer, optional): An instance of PAIGAuthorizer. Defaults to Depends(PAIGAuthorizerService).
        """
        self.paig_authorizer = paig_authorizer

    async def post_authorize(self, authz_service_request: AuthzServiceRequest, tenant_id) -> AuthzServiceResponse:
        """
        Sends an authorization request and returns the response.

        Args:
            authz_service_request (AuthzServiceRequest): The authorization request.
            tenant_id: The tenant id.

        Returns:
            AuthzServiceResponse: The authorization response.
        """
        tranformed_authz_request = self.transform_authz_request(authz_service_request)
        authz_response = await self.paig_authorizer.authorize(tranformed_authz_request)
        logger.debug(f"Reason: {authz_response.reason}")
        return self.transform_authz_response(authz_response)

    async def post_authorize_vectordb(self, vectordb_auth_req: AuthorizeVectorDBRequest, tenant_id):
        """
        Sends a VectorDB authorization request and returns the response.

        Args:
            vectordb_auth_req (AuthorizeVectorDBRequest): The VectorDB authorization request.
            tenant_id: The tenant id.

        Returns:
            AuthorizeVectorDBResponse: The VectorDB authorization response.
        """
        tranformed_vector_db_authz_request = self.transform_vector_db_authz_request(vectordb_auth_req)
        vectordb_response = await self.paig_authorizer.authorize_vector_db(tranformed_vector_db_authz_request)
        if not vectordb_response.reason:
            logger.debug(f"Reason: {vectordb_response.reason}")
        return self.transform_vector_db_authz_response(vectordb_response)

    def transform_authz_request(self, authz_service_request: AuthzServiceRequest) -> AuthzRequest:
        """
        Transforms an AuthzServiceRequest into an AuthzRequest.

        Args:
            authz_service_request (AuthzServiceRequest): The authorization service request.

        Returns:
            AuthzRequest: The transformed authorization request.
        """
        authz_request: AuthzRequest = AuthzRequest()
        authz_request.conversation_id = authz_service_request.conversationId
        authz_request.request_id = authz_service_request.requestId
        authz_request.thread_id = authz_service_request.threadId
        authz_request.sequence_number = authz_service_request.sequenceNumber
        authz_request.request_date_time = authz_service_request.requestDateTime
        authz_request.application_key = authz_service_request.applicationKey
        authz_request.client_application_key = authz_service_request.clientApplicationKey
        authz_request.request_type = authz_service_request.requestType
        authz_request.traits = authz_service_request.traits
        authz_request.user_id = authz_service_request.userId
        authz_request.enforce = authz_service_request.enforce
        authz_request.context = authz_service_request.context
        return authz_request

    def transform_authz_response(self, authz_response: AuthzResponse) -> AuthzServiceResponse:
        """
        Transforms an AuthzResponse into an AuthzServiceResponse.

        Args:
            authz_response (AuthzResponse): The authorization response.

        Returns:
            AuthzServiceResponse: The transformed authorization service response.
        """
        res_data = {
            "authorized": authz_response.authorized,
            "enforce": authz_response.enforce,
            "requestId": authz_response.request_id,
            "auditId": None,  # Assuming auditId is not present in AuthzResponse and needs a default value
            "applicationName": authz_response.application_name,
            "maskedTraits": authz_response.masked_traits,
            "context": authz_response.context,
            "paigPolicyIds": authz_response.paig_policy_ids,
            "statusCode": authz_response.status_code,
            "statusMessage": authz_response.status_message,
            "userId": authz_response.user_id
        }
        return AuthzServiceResponse(res_data)

    def transform_vector_db_authz_request(self, vectordb_auth_req: AuthorizeVectorDBRequest) -> VectorDBAuthzRequest:
        """
        Transforms an AuthorizeVectorDBRequest into a VectorDBAuthzRequest.

        Args:
            vectordb_auth_req (AuthorizeVectorDBRequest): The VectorDB authorization request.

        Returns:
            VectorDBAuthzRequest: The transformed VectorDB authorization request.
        """
        vectordb_authz_request: VectorDBAuthzRequest = VectorDBAuthzRequest()
        vectordb_authz_request.user_id = vectordb_auth_req.userId
        vectordb_authz_request.application_key = vectordb_auth_req.applicationKey
        return vectordb_authz_request

    def transform_vector_db_authz_response(self, vectordb_response: VectorDBAuthzResponse) -> AuthorizeVectorDBResponse:
        """
        Transforms a VectorDBAuthzResponse into an AuthorizeVectorDBResponse.

        Args:
            vectordb_response (VectorDBAuthzResponse): The VectorDB authorization response.

        Returns:
            AuthorizeVectorDBResponse: The transformed VectorDB authorization response.
        """
        res_data = {
            "vectorDBPolicyInfo": vectordb_response.vector_db_policy_info,
            "vectorDBId": vectordb_response.vector_db_id,
            "vectorDBName": vectordb_response.vector_db_name,
            "vectorDBType": vectordb_response.vector_db_type,
            "userEnforcement": vectordb_response.user_enforcement,
            "groupEnforcement": vectordb_response.group_enforcement,
            "filterExpression": vectordb_response.filter_expression
        }
        return AuthorizeVectorDBResponse(res_data)
