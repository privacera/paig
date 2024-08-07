import pytest
from api.authz.authorizer.paig_authorizer import PAIGAuthorizer
from api.shield.client.authz_service_rest_http_client import HttpAuthzClient
from api.shield.client.local_authz_service_client import LocalAuthzClient
from api.shield.utils import config_utils
from api.shield.factory.authz_service_client_factory import AuthzServiceClientFactory


class TestAuthzServiceClientFactory:

    @pytest.fixture(autouse=True)
    def setup_method(self, mocker):
        # Mock the PAIGAuthorizerService dependency
        self.mock_paig_authorizer = mocker.Mock(spec=PAIGAuthorizer)
        # Create an instance of the factory with the mocked PAIGAuthorizerService
        self.factory = AuthzServiceClientFactory()

    def test_get_http_authz_service_client(self, mocker):
        side_effect = lambda prop, default_value=None: {
            "authz_base_url": "base_url",
            "authz_client": "http"
        }.get(prop, default_value)
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Call the method to be tested
        client = self.factory.get_authz_service_client()

        # Assert that the returned client is an instance of HttpAuthzClient
        assert isinstance(client, HttpAuthzClient)

    def test_get_local_authz_service_client(self, mocker):
        # Mock the get_property_value to return 'local'
        mock_get_property_value = mocker.patch.object(config_utils, 'get_property_value', return_value='local')

        # Call the method to be tested
        client = self.factory.get_authz_service_client()

        # Assert that the returned client is an instance of LocalAuthzClient
        assert isinstance(client, LocalAuthzClient)
        mock_get_property_value.assert_called_once_with('authz_client', 'local')

    def test_get_invalid_authz_service_client(self, mocker):
        # Mock the get_property_value to return an invalid value
        mock_get_property_value = mocker.patch.object(config_utils, 'get_property_value', return_value='invalid')

        # Assert that an exception is raised when calling the method
        with pytest.raises(Exception) as exc_info:
            self.factory.get_authz_service_client()

        # Check that the exception message is correct
        assert str(exc_info.value) == "Invalid service type"
        mock_get_property_value.assert_called_once_with('authz_client', 'local')
