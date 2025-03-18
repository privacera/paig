import pytest
from api.shield.client.local_governance_service_client import LocalGovernanceServiceClient

class TestLocalGovernanceServiceClient:

    # Returns guardrails list when application exists with guardrails
    @pytest.mark.asyncio
    async def test_returns_guardrails_list_when_application_exists_with_guardrails(self, mocker):
        # Arrange
        mock_app_service = mocker.AsyncMock()
        mock_app = mocker.MagicMock()
        mock_app.guardrails = ["guardrail1", "guardrail2"]
        mock_app_service.get_ai_application_by_application_key.return_value = mock_app

        mocker.patch('api.shield.client.local_governance_service_client.SingletonDepends',
                     return_value=mock_app_service)

        client = LocalGovernanceServiceClient()

        # Act
        result = await client.get_application_guardrail_name("tenant1", "app_key1")

        # Assert
        assert result == ["guardrail1", "guardrail2"]
        mock_app_service.get_ai_application_by_application_key.assert_called_once_with("app_key1")

    # Returns empty list when application exists but has no guardrails
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_application_exists_without_guardrails(self, mocker):
        # Arrange
        mock_app_service = mocker.AsyncMock()
        mock_app = mocker.MagicMock()
        mock_app.guardrails = []
        mock_app_service.get_ai_application_by_application_key.return_value = mock_app

        mocker.patch('api.shield.client.local_governance_service_client.SingletonDepends',
                     return_value=mock_app_service)

        client = LocalGovernanceServiceClient()

        # Act
        result = await client.get_application_guardrail_name("tenant1", "app_key1")

        # Assert
        assert result == []
        mock_app_service.get_ai_application_by_application_key.assert_called_once_with("app_key1")

    # Successfully initializes with AIAppService dependency
    def test_successfully_initializes_with_aiapp_service_dependency(self, mocker):
        # Arrange
        mock_app_service = mocker.MagicMock()
        mocker.patch('api.shield.client.local_governance_service_client.SingletonDepends',
                     return_value=mock_app_service)

        # Act
        client = LocalGovernanceServiceClient()

        # Assert
        assert client.ai_application_service == mock_app_service

    # Returns empty list when application_key doesn't exist
    @pytest.mark.asyncio
    async def test_returns_empty_list_when_application_key_does_not_exist(self, mocker):
        # Arrange
        mock_app_service = mocker.AsyncMock()
        mock_app_service.get_ai_application_by_application_key.return_value = None

        mocker.patch('api.shield.client.local_governance_service_client.SingletonDepends',
                     return_value=mock_app_service)

        client = LocalGovernanceServiceClient()

        # Act
        result = await client.get_application_guardrail_name("tenant1", "non_existent_key")

        # Assert
        assert result == []
        mock_app_service.get_ai_application_by_application_key.assert_called_once_with("non_existent_key")

    # Handles None value in result.guardrails
    @pytest.mark.asyncio
    async def test_handles_none_value_in_result_guardrails(self, mocker):
        # Arrange
        mock_app_service = mocker.AsyncMock()
        mock_app = mocker.MagicMock()
        mock_app.guardrails = None
        mock_app_service.get_ai_application_by_application_key.return_value = mock_app

        mocker.patch('api.shield.client.local_governance_service_client.SingletonDepends',
                     return_value=mock_app_service)

        client = LocalGovernanceServiceClient()

        # Act
        result = await client.get_application_guardrail_name("tenant1", "app_key1")

        # Assert
        assert result == []
        mock_app_service.get_ai_application_by_application_key.assert_called_once_with("app_key1")

    # Handles empty guardrails list in application
    @pytest.mark.asyncio
    async def test_handles_empty_guardrails_list_in_application(self, mocker):
        # Arrange
        mock_app_service = mocker.AsyncMock()
        mock_app = mocker.MagicMock()
        mock_app.guardrails = []
        mock_app_service.get_ai_application_by_application_key.return_value = mock_app

        mocker.patch('api.shield.client.local_governance_service_client.SingletonDepends',
                     return_value=mock_app_service)

        client = LocalGovernanceServiceClient()

        # Act
        result = await client.get_application_guardrail_name("tenant1", "app_key1")

        # Assert
        assert result == []
        assert isinstance(result, list)
        mock_app_service.get_ai_application_by_application_key.assert_called_once_with("app_key1")

    # Processes application_key with special characters
    @pytest.mark.asyncio
    async def test_processes_application_key_with_special_characters(self, mocker):
        # Arrange
        mock_app_service = mocker.AsyncMock()
        mock_app = mocker.MagicMock()
        mock_app.guardrails = ["guardrail1"]
        mock_app_service.get_ai_application_by_application_key.return_value = mock_app

        mocker.patch('api.shield.client.local_governance_service_client.SingletonDepends',
                     return_value=mock_app_service)

        client = LocalGovernanceServiceClient()
        special_key = "app-key_123!@#$%^&*()"

        # Act
        result = await client.get_application_guardrail_name("tenant1", special_key)

        # Assert
        assert result == ["guardrail1"]
        mock_app_service.get_ai_application_by_application_key.assert_called_once_with(special_key)