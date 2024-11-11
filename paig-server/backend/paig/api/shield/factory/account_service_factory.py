from api.shield.utils import config_utils
from core.utils import SingletonDepends


class AccountServiceFactory:
    """
    Factory class for creating account service client instances based on configuration.

    Methods:
        get_account_service_client():
            Returns an instance of an account service client based on the configured client type.
    """

    def get_account_service_client(self):
        """
        Returns an instance of an account service client based on the configured client type.

        Returns:
            object: Instance of an account service client.

        Raises:
            Exception: If an invalid service type is configured in the application.
        """
        client_type = config_utils.get_property_value('account_service_client', 'local')
        match client_type:
            case "http":
                from api.shield.client.http_account_service_client import HttpAccountServiceClient
                return SingletonDepends(HttpAccountServiceClient)
            case "local":
                from api.shield.client.local_account_service_client import LocalAccountServiceClient
                return SingletonDepends(LocalAccountServiceClient)
            case _:
                raise Exception(
                    f"Invalid service type: '{client_type}'. Expected 'http' or 'local'. "
                    "Please configure the 'account_service_client' property with a valid service type."
                )
