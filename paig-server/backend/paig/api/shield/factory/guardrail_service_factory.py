from api.shield.utils import config_utils
from core.utils import SingletonDepends


class GuardrailServiceFactory:
    """
    Factory class for creating guardrail service client instances based on configuration.

    Methods:
        get_guardrail_service_client():
            Returns an instance of an guardrail service client based on the configured client type.
    """

    def get_guardrail_service_client(self):
        """
        Returns an instance of an guardrail service client based on the configured client type.

        Returns:
            object: Instance of an guardrail service client.

        Raises:
            Exception: If an invalid service type is configured in the application.
        """
        client_type = config_utils.get_property_value('guardrail_service_client', 'local')
        match client_type:
            case "http":
                from api.shield.client.http_guardrail_service_client import HttpGuardrailServiceClient
                return SingletonDepends(HttpGuardrailServiceClient)
            case "local":
                from api.shield.client.local_guardrail_service_client import LocalGuardrailServiceClient
                return SingletonDepends(LocalGuardrailServiceClient)
            case _:
                raise Exception(
                    f"Invalid service type: '{client_type}'. Expected 'http' or 'local'. "
                    "Please configure the 'guardrail_service_client' property with a valid service type."
                )
