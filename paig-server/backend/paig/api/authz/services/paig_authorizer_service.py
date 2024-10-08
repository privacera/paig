
from api.authz.authorizer.backend.rds_based_paig_authorizer import AsyncRDSBasedPaigAuthorizer
from paig_authorizer_core.async_paig_authorizer import AsyncPAIGAuthorizer
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from core.utils import SingletonDepends


class AuthorizeRequestValidator:
    """
    Validator class for validating authorize requests.

    Args:
        paig_authorizer (PAIGAuthorizer): The authorizer used to authorize requests.
    """

    def __init__(self, paig_authorizer: AsyncPAIGAuthorizer = SingletonDepends(AsyncRDSBasedPaigAuthorizer)):
        self.paig_authorizer = paig_authorizer

    # noinspection PyMethodMayBeStatic
    async def validate_authorize_request(self, request: AuthzRequest):
        """
        Validate an authorize request.

        Args:
            request (AuthzRequest): The request to validate.
        """
        from core.utils import validate_string_data, validate_id, validate_required_data

        validate_string_data(request.request_id, "Request ID")
        validate_string_data(request.thread_id, "Thread ID")
        validate_id(request.sequence_number, "Sequence Number")
        validate_string_data(request.application_key, "Application Key")
        validate_string_data(request.client_application_key, "Client Application Key")
        validate_string_data(request.user_id, "User ID")
        validate_string_data(request.request_type, "Request Type")
        # Not validating traits and traits can be blank sometimes, still we need to check if user has access to
        # application
        # validate_required_data(request.traits, "Traits")
        validate_required_data(request.request_date_time, "Request Date Time")

    # noinspection PyMethodMayBeStatic
    async def validate_vector_db_authorize_request(self, request: VectorDBAuthzRequest):
        """
        Validate a vector DB authorize request.

        Args:
            request (VectorDBAuthzRequest): The request to validate.
        """
        from core.utils import validate_string_data

        validate_string_data(request.user_id, "User ID")
        validate_string_data(request.application_key, "Application Key")


class PAIGAuthorizerService:
    """
    Service class for the PAIG authorizer.

    Args:
        paig_authorizer (PAIGAuthorizer): The authorizer used to authorize requests.
        authorize_request_validator (AuthorizeRequestValidator): The validator used to validate authorize requests.
    """

    def __init__(self, paig_authorizer: AsyncPAIGAuthorizer = SingletonDepends(AsyncRDSBasedPaigAuthorizer),
                 authorize_request_validator: AuthorizeRequestValidator = SingletonDepends(AuthorizeRequestValidator)):
        self.paig_authorizer = paig_authorizer
        self.authorize_request_validator = authorize_request_validator

    async def authorize(self, request: AuthzRequest) -> AuthzResponse:
        """
        Authorize a request.

        Args:
            request (AuthzRequest): The request to authorize.

        Returns:
            AuthzResponse: The response to the request.
        """
        await self.authorize_request_validator.validate_authorize_request(request)
        return await self.paig_authorizer.authorize(request)

    async def authorize_vector_db(self, request: VectorDBAuthzRequest) -> VectorDBAuthzResponse:
        """
        Authorize a vector DB request.

        Args:
            request (VectorDBAuthzRequest): The request to authorize.

        Returns:
            VectorDBAuthzResponse: The response to the request
        """
        await self.authorize_request_validator.validate_vector_db_authorize_request(request)
        return await self.paig_authorizer.authorize_vector_db(request)
