from api.shield.client.authz_service_rest_http_client import HttpAuthzClient
from api.shield.client.local_authz_service_client import LocalAuthzClient
from api.shield.utils import config_utils
from core.utils import SingletonDepends


class AuthzServiceClientFactory:
    """
    A factory class for creating authorization service clients.

    Methods:
        get_authz_service_client(client_type: str):
            Returns an instance of the specified authorization service client.
    """

    def get_authz_service_client(self):
        """
        Returns:
            An instance of the specified authorization service client.

        Raises:
            Exception: If the client_type is not "http" or "local".
        """
        client_type = config_utils.get_property_value('authz_client', 'local')
        match client_type:
            case "http":
                return SingletonDepends(HttpAuthzClient)
            case "local":
                return SingletonDepends(LocalAuthzClient)
            case _:
                raise Exception("Invalid service type")
