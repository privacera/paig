from api.shield.utils import config_utils
from core.utils import SingletonDepends


class GovernanceServiceFactory:
    """
    Factory class for creating governance service client instances based on configuration.

    Methods:
        get_governance_service_client():
            Returns an instance of an governance service client based on the configured client type.
    """

    def get_governance_service_client(self):
        """
        Returns an instance of an governance service client based on the configured client type.

        Returns:
            object: Instance of an governance service client.

        Raises:
            Exception: If an invalid service type is configured in the application.
        """
        client_type = config_utils.get_property_value('governance_service_client', 'local')
        match client_type:
            case "http":
                from api.shield.client.http_governance_service_client import HttpGovernanceServiceClient
                return SingletonDepends(HttpGovernanceServiceClient)
            case "local":
                from api.shield.client.local_governance_service_client import LocalGovernanceServiceClient
                return SingletonDepends(LocalGovernanceServiceClient)
            case _:
                raise Exception(
                    f"Invalid service type: '{client_type}'. Expected 'http' or 'local'. "
                    "Please configure the 'governance_service_client' property with a valid service type."
                )
