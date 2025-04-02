import logging

from paig_common.async_base_rest_http_client import AsyncBaseRESTHttpClient
from api.shield.utils.custom_exceptions import ShieldException

from api.shield.utils import config_utils
from api.shield.interfaces.guardrail_service_interface import IGuardrailServiceClient
from api.guardrails.api_schemas.guardrail import GuardrailView

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

           get_guardrail_info_by_id(tenant_id: str, guardrail_id: int):
                Retrieves Guardrail Config details for the specific tenant and guardrail id from guardrail service api

           get_guardrail_info_by_name(tenant_id: str, guardrail_name: str):
                Retrieves Guardrail Config details for the specified tenant and guardrail name from guardrail service api
       """

    def __init__(self):
        """
        Initialize the client instance with the base URL from configuration.
        """
        super().__init__(config_utils.get_property_value("guardrail_service_base_url"))
        self.url = config_utils.get_property_value("guardrail_service_get_guardrail_endpoint")

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

    async def get_guardrail_info_by_id(self, tenant_id: str, guardrail_id: int) -> dict:
        """
        Retrieve Guardrail Config details for the specified guardrail id from the Guardrail service API.
        :param guardrail_id:
        :param tenant_id:
        :return:
        """
        logger.debug(f"Using base-url={self.baseUrl} uri={self.url} for tenant-id={tenant_id} and guardrail-id={guardrail_id}")

        try:
            response = await self.get(
                url=self.url+"/"+str(guardrail_id),
                headers=self.get_headers(tenant_id),
                params={"extended": "true"}
            )
            logger.debug(f"response received: {response.__str__()}")

            if response.status_code != 200:
                raise ShieldException(f"Failed to fetch guardrail details for tenant {tenant_id} guardrail_id: {guardrail_id}. "
                                      f"Status code: {response.status}, Response: {response.text}")
            guardrail_info : GuardrailView = GuardrailView(**response.json())
            return guardrail_info.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        except Exception as ex:
            logger.error(f"Request get_guardrail_info_by_id({tenant_id}, {guardrail_id}) failed with error: {ex}")
            raise ShieldException(ex.args[0])

    async def get_guardrail_info_by_name(self, tenant_id, guardrail_name) -> dict:
        """
        Retrieve Guardrail Config details for the specified guardrail name from the Guardrail service API.
        :param tenant_id:
        :param guardrail_name:
        :return:
        """
        logger.debug(f"Using base-url={self.baseUrl} uri={self.url} for tenant-id={tenant_id} and guardrail-name={guardrail_name}")

        try:
            response = await self.get(
                url=self.url,
                headers=self.get_headers(tenant_id),
                params={"name": guardrail_name[0],
                        "extended": "true",
                        "exactMatch": "true"}
            )
            logger.debug(f"response received: {response.__str__()}")

            if response.status_code != 200:
                raise ShieldException(f"Failed to fetch guardrail details for tenant {tenant_id} guardrail_name: {guardrail_name}. "
                                      f"Status code: {response.status_code}, Response: {response.text}")
            response_content = response.json().get("content", {})
            guardrail_info : GuardrailView = GuardrailView(**response_content[0])
            return guardrail_info.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        except Exception as ex:
            logger.error(f"Request get_guardrail_info_by_name({tenant_id}, {guardrail_name}) failed with error: {ex}")
            raise ShieldException(ex.args[0])