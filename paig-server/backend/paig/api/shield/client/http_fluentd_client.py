import logging

from api.shield.client.base_rest_http_client import BaseRESTHttpClient
from api.shield.utils import config_utils
from api.shield.utils.custom_exceptions import ShieldException

logger = logging.getLogger(__name__)


class FluentdRestHttpClient(BaseRESTHttpClient):
    """
      FluentdRestHttpClient handles interactions with the Fluentd logging service,
      allowing messages to be logged via HTTP requests.
      """
    def __init__(self):
        """
        Initializes the FluentdRestHttpClient with configuration values for base URL,
        connection timeout, request timeout, and the audit tag.
        """
        super().__init__(config_utils.get_property_value('fluentd_base_url'))
        self.connection_timeout = config_utils.get_property_value_int('http_connection_timeout_ms', 2000) / 1000
        self.request_timeout = config_utils.get_property_value_int('http_request_timeout_ms', 5000) / 1000
        self.audit_tag = config_utils.get_property_value('fluentd_tag', 'paig_shield_audits')

    @staticmethod
    def get_headers():
        """
        Generates the necessary headers for logging requests.

        Returns:
            dict: A dictionary of headers including the PAIG API key if available.
        """
        paig_key = config_utils.get_property_value('paig_api_key')
        if paig_key is None:
            return {}

        return {"x-paig-api-key": paig_key}

    def log_message(self, message: str):
        """
        Sends a log message to the Fluentd service.

        Args:
            message (str): The message to be logged.

        Raises:
            ShieldException: If an error occurs while logging the message.
        """

        logger.debug(f"Using base-url={self.baseUrl} , tag={self.audit_tag} and logging message {message}")
        try:
            response = self.post(
                url="/" + self.audit_tag,
                headers=self.get_headers(),
                json=message
            )
            logger.debug(f"logging response received: {response.__str__()}")
            if response.status_code == 200:
                logger.debug(f"Successfully logged message: {message}")
            else:
                logger.error(f"Failed to log message: {message} with response: {response.__str__()}")
                raise ShieldException(f"Failed to log message: {message} with response: {response.__str__()}")
        except Exception as ex:
            logger.error(f"Failed to log message: {message} with error: {ex}")
            raise ShieldException(f"Failed to log message: {message} with error: {ex}")
