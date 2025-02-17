import logging


from paig_common.async_base_rest_http_client import AsyncBaseRESTHttpClient
from api.shield.utils.custom_exceptions import ShieldException

from api.shield.utils import config_utils
from api.shield.interfaces.guardrail_service_interface import IGuardrailServiceClient

logger = logging.getLogger(__name__)


class HttpGuardrailServiceClient(AsyncBaseRESTHttpClient, IGuardrailServiceClient):
    """
       HTTP client for interacting with an Guardrail service API, implementing the IGuardrailServiceClient interface.

       This client supports fetching guardrail details from a remote guardrail service using HTTP requests.

       Methods:
           init_singleton():
               Initializes the singleton instance of the client with the base URL from configuration.

           get_headers(tenant_id: str):
               Returns headers for API requests based on the provided tenant_id.

           get_guardrail_info(tenant_id: str, guardrail_id: int):
               Retrieves all the guardrail details for a specific tenant from the Guardrail service API.
       """

    def __init__(self):
        """
        Initialize the client instance with the base URL from configuration.
        """
        super().__init__(config_utils.get_property_value("guardrail_service_base_url"))

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

    async def get_guardrail_info_by_id(self, tenant_id: str, guardrail_id: int):
        """
        Retrieve Guardrail Config details for the specified guardrail id from the Guardrail service API.
        :param guardrail_id:
        :param tenant_id:
        :return:
        """
        url = config_utils.get_property_value("guardrail_service_get_guardrail_configs_endpoint")
        logger.debug(f"Using base-url={self.baseUrl} uri={url} for tenant-id={tenant_id} and guardrail-id={guardrail_id}")

        response = await self.get(
            url=url+"/"+str(guardrail_id),
            headers=self.get_headers(tenant_id),
            params={"extended": "true"}
        )
        if response.status != 200:
            raise ShieldException(f"Failed to fetch guardrail details for guardrail_id: {guardrail_id}. "
                                  f"Status code: {response.status}, Response: {response.text}")
        return response.json()

    async def get_guardrail_info_by_name(self, tenant_id, guardrail_name):
        """
        Retrieve Guardrail Config details for the specified guardrail name from the Guardrail service API.
        :param tenant_id:
        :param guardrail_name:
        :return:
        """
        url = config_utils.get_property_value("guardrail_service_get_guardrail_endpoint")
        logger.debug(f"Using base-url={self.baseUrl} uri={url} for tenant-id={tenant_id} and guardrail-name={guardrail_name}")

        response = await self.get(
            url=url,
            headers=self.get_headers(tenant_id),
            params={"guardrail_name": guardrail_name,
                    "extended": "true",
                    "exactmatch": "true"}
        )
        if response.status != 200:
            raise ShieldException(f"Failed to fetch guardrail details for guardrail_name: {guardrail_name}. "
                                  f"Status code: {response.status}, Response: {response.text}")
        return response.json()