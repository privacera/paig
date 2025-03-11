import pytest
from api.shield.client.http_guardrail_service_client import HttpGuardrailServiceClient
from api.shield.utils.custom_exceptions import ShieldException
from unittest.mock import Mock


class TestHttpGuardrailServiceClient:


    def test_initialization_with_correct_base_url(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', return_value='http://paig-server.com')
        client = HttpGuardrailServiceClient()
        assert client.baseUrl == 'http://paig-server.com'


    def test_get_headers_with_tenant_id_and_api_key(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=lambda key: 'test-api-key' if key == 'paig_api_key' else None)
        headers = HttpGuardrailServiceClient.get_headers('tenant123')
        assert headers == {"x-paig-api-key": "test-api-key"}


    def test_get_headers_without_api_key(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', return_value=None)
        headers = HttpGuardrailServiceClient.get_headers('tenant123')
        assert headers == {"x-tenant-id": "tenant123", "x-user-role": "OWNER"}


    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Skipping this test case as we are running in OSS mode.")
    async def test_get_guardrail_info_by_name_success(self, mocker):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": [{"name": "guardrail", "details": "details"}]}
        mocker.patch.object(HttpGuardrailServiceClient, 'get', return_value=mock_response)
        client = HttpGuardrailServiceClient()
        result = await client.get_guardrail_info_by_name('tenant123', 'guardrailName')
        assert result == {'name': 'guardrail', 'details': 'details'}


    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Skipping this test case as we are running in OSS mode.")
    async def test_get_guardrail_info_by_name_non_200_status(self, mocker):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mocker.patch.object(HttpGuardrailServiceClient, 'get', return_value=mock_response)
        client = HttpGuardrailServiceClient()
        with pytest.raises(ShieldException) as excinfo:
            await client.get_guardrail_info_by_name('tenant123', 'guardrailName')
        assert "Not Found" in str(excinfo.value)


    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Skipping this test case as we are running in OSS mode.")
    async def test_get_guardrail_info_by_name_error(self, mocker):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mocker.patch.object(HttpGuardrailServiceClient, 'get', return_value=mock_response)
        client = HttpGuardrailServiceClient()
        with pytest.raises(ShieldException) as excinfo:
            await client.get_guardrail_info_by_name('tenant123', 'guardrailName')
        assert "Internal Server Error" in str(excinfo.value)


    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Skipping this test case as we are running in OSS mode.")
    async def test_get_guardrail_info_by_name_unexpected_exception(self, mocker):
        mocker.patch.object(HttpGuardrailServiceClient, 'get', side_effect=Exception("Unexpected Error"))
        client = HttpGuardrailServiceClient()
        with pytest.raises(ShieldException) as excinfo:
            await client.get_guardrail_info_by_name('tenant123', 'guardrailName')
        assert "Unexpected Error" in str(excinfo.value)


    @pytest.mark.asyncio
    async def test_get_guardrail_info_by_id_non_200_status(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=lambda
            key: 'http://paig-server/guardrail' if key == 'guardrail_service_get_guardrail_configs_endpoint' else None)

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mocker.patch.object(HttpGuardrailServiceClient, 'get', return_value=mock_response)

        client = HttpGuardrailServiceClient()
        with pytest.raises(ShieldException) as excinfo:
            await client.get_guardrail_info_by_id('tenant123', 1)
        assert "Not Found" in str(excinfo.value)


    @pytest.mark.asyncio
    async def test_get_guardrail_info_by_id_success(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=lambda
            key: 'http://paig-server/guardrail' if key == 'guardrail_service_get_guardrail_configs_endpoint' else None)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"guardrail": {"key": "value"}}
        mocker.patch.object(HttpGuardrailServiceClient, 'get', return_value=mock_response)

        client = HttpGuardrailServiceClient()
        result = await client.get_guardrail_info_by_id('tenant123', 1)
        assert result == {"guardrail": {"key": "value"}}


    @pytest.mark.asyncio
    async def test_get_guardrail_info_by_name_empty_response(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=lambda
            key: 'http://paig-server/guardrail' if key == 'guardrail_service_get_guardrail_configs_endpoint' else None)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": []}
        mocker.patch.object(HttpGuardrailServiceClient, 'get', return_value=mock_response)

        client = HttpGuardrailServiceClient()
        try:
            result = await client.get_guardrail_info_by_name('tenant123', 'guardrailName')
            assert result == {}
        except ShieldException:
            assert True