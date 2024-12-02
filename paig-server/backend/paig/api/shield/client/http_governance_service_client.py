import json
import logging


from paig_common.async_base_rest_http_client import AsyncBaseRESTHttpClient
from api.shield.utils.custom_exceptions import ShieldException

from api.shield.utils import config_utils
from api.shield.interfaces.governance_service_interface import IGovernanceServiceClient

logger = logging.getLogger(__name__)


class HttpGovernanceServiceClient(AsyncBaseRESTHttpClient, IGovernanceServiceClient):
    """
       HTTP client for interacting with an governance service API, implementing the IGovernanceServiceClient interface.

       This client supports fetching AWS Bedrock guardrail details from a remote service using HTTP requests.

       Methods:
           init_singleton():
               Initializes the singleton instance of the client with the base URL from configuration.

           get_headers(tenant_id: str):
               Returns headers for API requests based on the provided tenant_id.

           get_all_encryption_keys(tenant_id):
               Retrieves all AWS Bedrock guardrail details for a specific tenant from the governance service API.
       """

    def __init__(self):
        """
        Initialize the client instance with the base URL from configuration.
        """
        super().__init__(config_utils.get_property_value("governance_service_base_url"))

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
            return {"x-tenant-id": tenant_id, "x-user-role": "OWNER"}

        return {"x-paig-api-key": paig_key}

    async def get_aws_bedrock_guardrail_info(self, tenant_id, application_key):
        """
        Retrieve all AWS Bedrock guardrail details for a specific tenant and application from the governance service API.

        Args:
            tenant_id (str): Identifier of the tenant whose AWS Bedrock guardrail details are to be fetched.
            application_key (str): Identifier of the application for which AWS Bedrock guardrail details are to be fetched.

        Returns:
            dict: Dictionary containing AWS Bedrock guardrail details associated with the specified tenant_id and application_key.

        Raises:
            ShieldException: If the API request fails or returns a non-200 status code.
        """
        url = config_utils.get_property_value("governance_service_get_ai_app_endpoint")
        logger.debug(f"Using base-url={self.baseUrl} uri={url} for tenant-id={tenant_id} and application-key={application_key}")

        try:

            response = await self.get(
                url=url,
                headers=self.get_headers(tenant_id),
                params={"applicationKey": application_key}
            )

            logger.debug(f"response received: {response.__str__()}")

            if response.status_code == 200:
                response_content = response.json().get("content")[0]
                guardrail_details = response_content.get("guardrailDetails", "{}") if response_content else "{}"
                return json.loads(guardrail_details)
            else:
                error_message = (f"Request get_aws_bedrock_guardrail_info({tenant_id}, {application_key}) failed "
                                 f"with status code {response.status_code}: {response.text}")
                raise ShieldException(error_message)
        except Exception as ex:
            logger.error(f"Request get_aws_bedrock_guardrail_info({tenant_id}, {application_key}) failed with error: {ex}")
            raise ShieldException(ex.args[0])
