import logging
import time
from paig_common.async_base_rest_http_client import AsyncBaseRESTHttpClient
from api.shield.utils.custom_exceptions import ShieldException

from api.shield.utils import config_utils
from api.shield.interfaces.account_service_interface import IAccountServiceClient
from opentelemetry import metrics

logger = logging.getLogger(__name__)
meter = metrics.get_meter(__name__)


class HttpAccountServiceClient(AsyncBaseRESTHttpClient, IAccountServiceClient):
    """
       HTTP client for interacting with an account service API, implementing the IAccountServiceClient interface.

       This client supports fetching encryption keys from a remote service using HTTP requests.

       Methods:
           init_singleton():
               Initializes the singleton instance of the client with the base URL from configuration.

           get_headers(tenant_id: str):
               Returns headers for API requests based on the provided tenant_id.

           get_all_encryption_keys(tenant_id):
               Retrieves all encryption keys for a specific tenant from the account service API.
       """

    def __init__(self):
        """
        Initialize the client instance with the base URL from configuration.
        """
        super().__init__(config_utils.get_property_value("account_service_base_url"))
        self.account_service_request_histogram = meter.create_histogram("account_service_request_duration", "ms",
                                                                        "Histogram for account_service request")

    @staticmethod
    def get_headers(tenant_id: str):
        """
        Return headers for API requests based on the provided tenant_id.

        Args:
            tenant_id (str): Identifier of the tenant for which headers are generated.

        Returns:
            dict: Headers dictionary containing necessary headers for API requests.
        """
        paig_key = config_utils.get_property_value('paig_api_key')
        if paig_key is None:
            return {"x-tenant-id": tenant_id, "x-user-role": "INTERNAL_SERVICE"}

        return {"x-paig-api-key": paig_key}

    async def get_all_encryption_keys(self, tenant_id):
        """
        Retrieve all encryption keys for a specific tenant from the account service API.

        Args:
            tenant_id (str): Identifier of the tenant whose encryption keys are to be fetched.

        Returns:
            dict: Dictionary containing encryption keys associated with the specified tenant_id.

        Raises:
            ShieldException: If the API request fails or returns a non-200 status code.
        """
        url = config_utils.get_property_value("account_service_get_key_endpoint")
        logger.debug(f"Using base-url={self.baseUrl} uri={url} for tenant-id={tenant_id}")
        request_start_time = time.perf_counter()
        response = None
        try:

            response = await self.get(
                url=url,
                headers=self.get_headers(tenant_id)
            )

            logger.debug(f"response received: {response.__str__()}")

            if response.status_code == 200:
                return response.json()
            else:
                error_message = (f"Request all_latest_encryption_key({tenant_id}) failed "
                                 f"with status code {response.status_code}: {response.text}")
                raise ShieldException(error_message)
        except Exception as ex:
            logger.error(f"Request all_latest_encryption_key({tenant_id}) failed with error: {ex}")
            raise ShieldException(ex.args[0])
        finally:
            self.account_service_request_histogram.record(round((time.perf_counter() - request_start_time) * 1000, 3),
                                                          {"path": url, "status": response.status_code,
                                                           "tenant_id": tenant_id,
                                                           "request_method": "GET"})
