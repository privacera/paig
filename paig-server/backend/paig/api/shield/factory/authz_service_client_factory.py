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
                from api.shield.client.http_authz_service_client import HttpAuthzClient
                return SingletonDepends(HttpAuthzClient)
            case "local":
                from api.shield.client.local_authz_service_client import LocalAuthzClient
                return SingletonDepends(LocalAuthzClient)
            case _:
                raise Exception("Invalid service type")
