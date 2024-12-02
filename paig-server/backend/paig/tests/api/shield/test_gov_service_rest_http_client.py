import pytest

from api.shield.client.http_governance_service_client import HttpGovernanceServiceClient
from api.shield.utils.custom_exceptions import ShieldException


class TestHttpGovernanceServiceClient:

    # Successfully initializes with the correct base URL from configuration
    def test_initialization_with_correct_base_url(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', return_value='http:#example.com')
        client = HttpGovernanceServiceClient()
        assert client.baseUrl == 'http:#example.com'

    # Correctly retrieves headers with tenant ID and API key
    def test_get_headers_with_tenant_id_and_api_key(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=lambda key: 'test-api-key' if key == 'paig_api_key' else None)
        headers = HttpGovernanceServiceClient.get_headers('tenant123')
        assert headers == {"x-paig-api-key": "test-api-key"}

    # Successfully fetches AWS Bedrock guardrail details with valid tenant and application keys
    @pytest.mark.asyncio
    async def test_fetch_guardrail_details_success(self, mocker):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": [{"guardrailDetails": '{"key": "value"}'}]}
        mocker.patch.object(HttpGovernanceServiceClient, 'get', return_value=mock_response)
        client = HttpGovernanceServiceClient()
        result = await client.get_aws_bedrock_guardrail_info('tenant123', 'appKey123')
        assert result == {"key": "value"}

    # Handles missing or invalid tenant ID gracefully
    @pytest.mark.asyncio
    async def test_handle_missing_or_invalid_tenant_id(self, mocker):
        mock_response = mocker.Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mocker.patch.object(HttpGovernanceServiceClient, 'get', return_value=mock_response)
        client = HttpGovernanceServiceClient()
        with pytest.raises(ShieldException) as excinfo:
            await client.get_aws_bedrock_guardrail_info('', 'appKey123')
        assert "Bad Request" in str(excinfo.value)

    # Manages scenarios where the API key is not set in configuration
    def test_no_api_key_in_configuration(self, mocker):
        mocker.patch('api.shield.utils.config_utils.get_property_value', return_value=None)
        headers = HttpGovernanceServiceClient.get_headers('tenant123')
        assert headers == {"x-tenant-id": "tenant123", "x-user-role": "OWNER"}

    # Deals with empty or malformed JSON responses
    @pytest.mark.asyncio
    async def test_handle_empty_or_malformed_json_response(self, mocker):
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"content": [{}]}
        mocker.patch.object(HttpGovernanceServiceClient, 'get', return_value=mock_response)
        client = HttpGovernanceServiceClient()
        result = await client.get_aws_bedrock_guardrail_info('tenant123', 'appKey123')
        assert result == {}

    # Handles non-200 HTTP status codes by raising ShieldException
    @pytest.mark.asyncio
    async def test_non_200_http_status_code_raises_exception(self, mocker):
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mocker.patch.object(HttpGovernanceServiceClient, 'get', return_value=mock_response)
        client = HttpGovernanceServiceClient()
        with pytest.raises(ShieldException) as excinfo:
            await client.get_aws_bedrock_guardrail_info('tenant123', 'appKey123')
        assert "Not Found" in str(excinfo.value)
