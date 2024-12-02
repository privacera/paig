from unittest.mock import Mock
from api.shield.utils.custom_exceptions import ShieldException

import pytest


class TestHttpAccountServiceClient:

    #  can get all encryption keys for a given tenant
    @pytest.mark.asyncio
    async def test_can_get_all_encryption_keys_for_given_tenant(self, mocker):
        from api.shield.client.http_account_service_client import HttpAccountServiceClient
        # Mock the necessary dependencies
        side_effect = lambda prop, default_value=None: {
            "account_service_base_url": "base_url",
            "account_service_get_key_endpoint": "/get_key_endpoint"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch.object(HttpAccountServiceClient, 'get', return_value=Mock(status_code=200, json=Mock(
            return_value=[{"key": "value"}])))

        # Create an instance of HttpAccountServiceClient
        account_service_client = HttpAccountServiceClient()

        # Call the method being tested
        tenant_id = "example_tenant"
        encryption_keys = await account_service_client.get_all_encryption_keys(tenant_id)

        # Assert that the necessary method was called
        account_service_client.get.assert_called_with(url="/get_key_endpoint", headers={"x-tenant-id": tenant_id,
                                                                                        "x-user-role": "INTERNAL_SERVICE"})
        assert encryption_keys == [{"key": "value"}], "The encryption keys should match the expected value"

    #  can get all encryption keys for a given tenant with paig api key
    @pytest.mark.asyncio
    async def test_can_get_all_encryption_keys_for_given_tenant_with_paig_api_key(self, mocker):
        from api.shield.client.http_account_service_client import HttpAccountServiceClient
        # Mock the necessary dependencies
        side_effect = lambda prop, default_value=None: {
            "account_service_base_url": "base_url",
            "account_service_get_key_endpoint": "/get_key_endpoint",
            "paig_api_key": "1234qwerty890"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch.object(HttpAccountServiceClient, 'get').return_value = Mock(status_code=200, json=Mock(
            return_value=[{"key": "value"}]))

        # Create an instance of HttpAccountServiceClient
        account_service_client = HttpAccountServiceClient()

        # Call the method being tested
        tenant_id = "example_tenant"
        encryption_keys = await account_service_client.get_all_encryption_keys(tenant_id)

        # Assert that the necessary method was called
        HttpAccountServiceClient.get.assert_called_with(url="/get_key_endpoint", headers={"x-paig-api-key":
                                                                                              "1234qwerty890"})
        assert encryption_keys == [{"key": "value"}], "The encryption keys should match the expected value"

    #  can get all encryption keys for a given tenant with no paig api key
    @pytest.mark.asyncio
    async def test_get_all_encryption_keys_with_error_response(self, mocker):
        from api.shield.client.http_account_service_client import HttpAccountServiceClient
        # Mock the necessary dependencies
        side_effect = lambda prop, default_value=None: {
            "account_service_base_url": "base_url",
            "account_service_get_key_endpoint": "/get_key_endpoint",
            "paig_api_key": "1234qwerty890"
        }.get(prop, default_value)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)
        mocker.patch('api.shield.utils.config_utils.get_property_value_int', side_effect=side_effect)
        mocker.patch('api.shield.utils.config_utils.get_property_value_float', side_effect=side_effect)
        mocker.patch.object(HttpAccountServiceClient, 'get', return_value=Mock(status_code=400, json=Mock(
            return_value=[{"key": "value"}])))

        # Create an instance of HttpAccountServiceClient
        account_service_client = HttpAccountServiceClient()

        # Call the method being tested
        tenant_id = "example_tenant"

        with pytest.raises(ShieldException) as e:
            await account_service_client.get_all_encryption_keys(tenant_id)

        print(f"\nGot exception=> {e.type}: {e.value}")
