import logging
import time

from paig_common.constants import X_TENANT_ID_HEADER, X_USER_ROLE_HEADER

from paig_common.async_base_rest_http_client import AsyncBaseRESTHttpClient
from api.shield.interfaces.authz_service_interface import IAuthzClient
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.vectordb_authz_response import AuthorizeVectorDBResponse
from api.shield.utils import config_utils
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.authz_service_request import AuthzServiceRequest
from api.shield.utils.custom_exceptions import ShieldException
from opentelemetry import metrics

logger = logging.getLogger(__name__)
meter = metrics.get_meter(__name__)


class HttpAuthzClient(AsyncBaseRESTHttpClient, IAuthzClient):
    """
      HttpAuthzClient is responsible for handling authorization requests
      """

    def __init__(self):
        """
        Initializes the HttpAuthzClient with the base URL for the authorization service.
        """
        super().__init__(config_utils.get_property_value('authz_base_url', "127.0.0.1:8080"))

        self.authz_request_histogram = meter.create_histogram("authz_request_duration", "ms", "Histogram for authz request")

    @staticmethod
    def get_headers(tenant_id: str, user_role: str):
        """
        Generates the necessary headers for the authorization requests.

        Parameters:
        tenant_id (str): The tenant ID.
        user_role (str): The user role.

        Returns:
        dict: A dictionary containing the required headers.
        """
        paig_key = config_utils.get_property_value('paig_api_key')
        if paig_key is None:
            return {X_TENANT_ID_HEADER: tenant_id, X_USER_ROLE_HEADER: user_role}

        return {"x-paig-api-key": paig_key}

    async def post_authorize(self, authz_req: AuthzServiceRequest, tenant_id: str) -> AuthzServiceResponse:
        """
        Sends an authorization request

        Args:
            authz_req (AuthzServiceRequest): The authorization request payload.
            tenant_id (str): The tenant ID.

        Returns:
            AuthzServiceResponse: The response from the authorization service.

        Raises:
            ShieldException: If an error occurs while processing the request.
        """
        request_start_time = time.perf_counter()
        url = config_utils.get_property_value('authz_authorize_endpoint')
        logger.debug(
            f"Using base-url={self.baseUrl} uri={url} for tenant-id={tenant_id} with user role = {authz_req.user_role}")

        logger.debug(f"AuthzServiceRequest: {authz_req.to_payload_dict()}")
        response = None
        try:
            response = await self.post(
                url=url,
                headers=self.get_headers(tenant_id, authz_req.user_role),
                json=authz_req.to_payload_dict()
            )
            logger.debug(f"AuthzServiceResponse: {response.__str__()}")

            if response.status_code == 200:
                return AuthzServiceResponse(response.json())
            else:
                logger.error(f"Privacera Shield Internal Error. Please contact Privacera Support. {response.text}")
                raise ShieldException(response.text)
        except Exception as ex:
            logger.error(f"Privacera Shield Internal Error. Please contact Privacera Support. {ex}")
            raise ShieldException(ex.args[0])
        finally:
            self.authz_request_histogram.record(round((time.perf_counter() - request_start_time) * 1000, 3),
                                                {"path": url, "status": response.status_code,
                                                 "tenant_id": tenant_id,
                                                 "request_method": "POST"})

    async def post_init_authz(self, tenant_id: str, user_role: str, **kwargs) -> None:
        """
        Initializes the authorization service for a specific tenant and user role.

        Args:
            tenant_id (str): The tenant ID.
            user_role (str): The user role.

        Raises:
            ShieldException: If an error occurs while processing the request.
        """
        request_start_time = time.perf_counter()
        url = config_utils.get_property_value('authz_init_endpoint')
        logger.debug(
            f"Using base-url={self.baseUrl} uri={url} for tenant-id={tenant_id}")
        response = None

        try:
            request_body = {}
            application_key = kwargs.get("application_key", None)
            if application_key:
                request_body["applicationKey"] = application_key

            response = await self.post(
                url=url,
                headers=self.get_headers(tenant_id, user_role),
                json=request_body
            )

            logger.debug(f"AuthzServiceResponse: {response.__str__()}")

            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"Privacera Shield Internal Error. Please contact Privacera Support. {response.text}")
                raise ShieldException(response.text)
        except Exception as ex:
            logger.error(f"Privacera Shield Internal Error. Please contact Privacera Support. {ex}")
            raise ShieldException(ex.args[0])
        finally:
            self.authz_request_histogram.record(round((time.perf_counter() - request_start_time) * 1000, 3),
                                                {"path": url, "status": response.status_code,
                                                 "tenant_id": tenant_id,
                                                 "request_method": "POST"})

    async def post_authorize_vectordb(self, authz_req: AuthorizeVectorDBRequest,
                                      tenant_id: str) -> AuthorizeVectorDBResponse:
        """
        Sends an authorization request for VectorDB operations .

        Args:
            authz_req (AuthorizeVectorDBRequest): The authorization request payload for VectorDB.
            tenant_id (str): The tenant ID.

        Returns:
            AuthorizeVectorDBResponse: The response from the authorization service.

        Raises:
            ShieldException: If an error occurs while processing the request.
        """
        request_start_time = time.perf_counter()
        url = config_utils.get_property_value('authz_vectordb_endpoint')
        logger.debug(
            f"Using base-url={self.baseUrl} uri={url} for tenant-id={tenant_id} with user role = {authz_req.user_role}")

        logger.debug(f"AuthorizeVectorDBRequest: {authz_req.to_payload_dict()}")
        response = None
        try:
            response = await self.post(
                url=url,
                headers=self.get_headers(tenant_id, authz_req.user_role),
                json=authz_req.to_payload_dict()
            )
            logger.debug(f"AuthorizeVectorDBResponse: {response.__str__()}")

            if response.status_code == 200:
                return AuthorizeVectorDBResponse(response.json())
            else:
                logger.error(f"Privacera Shield Internal Error. Please contact Privacera Support. {response.text}")
                raise ShieldException(response.text)
        except Exception as ex:
            logger.error(f"Privacera Shield Internal Error. Please contact Privacera Support. {ex}")
            raise ShieldException(ex.args[0])
        finally:
            self.authz_request_histogram.record(round((time.perf_counter() - request_start_time) * 1000, 3),
                                                {"path": url, "status": response.status_code,
                                                 "tenant_id": tenant_id,
                                                 "request_method": "POST"})
