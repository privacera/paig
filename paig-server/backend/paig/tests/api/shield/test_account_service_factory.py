import pytest

from api.shield.utils import config_utils
from api.shield.factory.account_service_factory import AccountServiceFactory


class TestAccountServiceFactory:

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.factory = AccountServiceFactory()

    def test_get_local_account_service_client(self, mocker):
        mock_get_property_value = mocker.patch.object(config_utils, 'get_property_value', return_value='local')

        client = self.factory.get_account_service_client()
        from api.shield.client.local_account_service_client import LocalAccountServiceClient
        assert isinstance(client, LocalAccountServiceClient)
        mock_get_property_value.assert_called_once_with('account_service_client', 'local')

    def test_get_http_account_service_client(self, mocker):
        from api.shield.client.http_account_service_client import HttpAccountServiceClient
        side_effect = lambda prop, default_value=None: {
            "account_service_base_url": "base_url",
            "account_service_client": "http"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        client = self.factory.get_account_service_client()

        assert isinstance(client, HttpAccountServiceClient)

    def test_get_invalid_account_service_client(self, mocker):
        mock_get_property_value = mocker.patch.object(config_utils, 'get_property_value', return_value='invalid')

        with pytest.raises(Exception) as exc_info:
            self.factory.get_account_service_client()

        assert "Invalid service type: 'invalid'. Expected 'http' or 'local'." in str(exc_info.value)
        mock_get_property_value.assert_called_once_with('account_service_client', 'local')
