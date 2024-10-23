import pytest
from unittest.mock import patch, MagicMock

from api.guardrails.providers import GuardrailConnection, GuardrailConfig, GuardrailProviderManager


@pytest.fixture
def mock_connections():
    """Fixture to provide a list of mock connections."""
    return [
        GuardrailConnection(name="AWS Connection 1", description="AWS Guardrail", guardrailProvider="AWS",
                            connectionDetails={"key": "value"})
    ]


@pytest.fixture
def mock_guardrail_configs():
    """Fixture to provide a list of mock guardrail configurations."""
    return [
        GuardrailConfig(status=1, guardrailProvider="AWS", guardrailProviderConnectionName="AWS Connection 1",
                        configType="topicPolicyConfig", configData={})
    ]


@pytest.fixture
def guardrail_provider_map():
    return {
        'aws': MagicMock(),
        'gcp': MagicMock(),
        'azure': MagicMock()
    }


@pytest.fixture
def create_guardrails_response():
    return {
        'aws': {"success": True},
        'gcp': {"success": False},
        'azure': {"success": True}
    }


@pytest.fixture
def successful_providers():
    return ['aws', 'azure']


@pytest.fixture
def unsuccessful_providers():
    return ['gcp']


@patch('api.guardrails.providers.backend.bedrock.BedrockGuardrailProvider')
def test_verify_guardrails_connection_details(mock_bedrock_provider, mock_connections):
    """Test verifying guardrail connection details."""
    mock_bedrock_provider.return_value.verify_connection_details.return_value = True

    result = GuardrailProviderManager.verify_guardrails_connection_details(mock_connections)

    assert result is True
    mock_bedrock_provider.return_value.verify_connection_details.assert_called_once()


@patch('api.guardrails.providers.backend.bedrock.BedrockGuardrailProvider')
def test_create_guardrail(mock_bedrock_provider, mock_connections, mock_guardrail_configs):
    """Test creating guardrails for a list of connections and configs."""
    mock_provider = mock_bedrock_provider.return_value
    mock_provider.create_guardrail.return_value = (True, {"guardrail_id": 1})

    result = GuardrailProviderManager.create_guardrail(mock_connections, mock_guardrail_configs)

    assert result["AWS"]["success"] is True
    assert "guardrail_id" in result["AWS"]["response"]
    mock_provider.create_guardrail.assert_called_once()


@pytest.mark.skip(reason="This can be enabled when more than one provider is added")
@patch('api.guardrails.providers.backend.bedrock.BedrockGuardrailProvider')
def test_create_guardrail_failure_rolls_back(mock_bedrock_provider, mock_connections, mock_guardrail_configs):
    """Test that if a guardrail creation fails, rollback (deletion) is triggered."""
    mock_provider = mock_bedrock_provider.return_value
    mock_provider.create_guardrail.side_effect = [(True, {"guardrail_id": 1}), (False, {"error": "failed"})]
    mock_provider.delete_guardrail.return_value = (True, {})

    mock_connections.append(GuardrailConnection(name="Azure Connection 1", description="Azure Guardrail",
                                                guardrailProvider="AZURE", connectionDetails={"key": "value"}))
    mock_guardrail_configs.append(
        GuardrailConfig(status=1, guardrailProvider="AZURE", guardrailProviderConnectionName="Azure Connection 1",
                        configType="topicPolicyConfig", configData={})
    )

    result = GuardrailProviderManager.create_guardrail(mock_connections, mock_guardrail_configs)

    assert result["AZURE"]["success"] is False
    mock_provider.delete_guardrail.assert_called_once()


@patch('api.guardrails.providers.backend.bedrock.BedrockGuardrailProvider')
def test_update_guardrail(mock_bedrock_provider, mock_connections, mock_guardrail_configs):
    """Test updating guardrails."""
    mock_provider = mock_bedrock_provider.return_value
    mock_provider.update_guardrail.return_value = (True, {"updated": True})

    create_guardrails_response = {"AWS": {"success": True, "response": {"guardrail_id": 1}}}

    result = GuardrailProviderManager.update_guardrail(mock_connections, create_guardrails_response,
                                                       mock_guardrail_configs)

    assert result["AWS"]["success"] is True
    assert result["AWS"]["response"]["updated"] is True
    mock_provider.update_guardrail.assert_called_once()


@patch('api.guardrails.providers.backend.bedrock.BedrockGuardrailProvider')
def test_delete_guardrail(mock_bedrock_provider, mock_connections):
    """Test deleting guardrails."""
    mock_provider = mock_bedrock_provider.return_value
    mock_provider.delete_guardrail.return_value = (True, {"deleted": True})

    create_guardrails_response = {"AWS": {"success": True, "response": {"guardrail_id": 1}}}

    result = GuardrailProviderManager.delete_guardrail(mock_connections, create_guardrails_response)

    assert result["AWS"]["success"] is True
    assert result["AWS"]["response"]["deleted"] is True
    mock_provider.delete_guardrail.assert_called_once()


def test_group_connections_by_provider(mock_connections):
    """Test grouping connections by provider."""
    grouped = GuardrailProviderManager._group_connections_by_provider(mock_connections)

    assert "AWS" in grouped
    assert grouped["AWS"].name == "AWS Connection 1"


def test_group_by_provider(mock_guardrail_configs):
    """Test grouping guardrail configurations by provider."""
    grouped = GuardrailProviderManager._group_by_provider(mock_guardrail_configs)

    assert "AWS" in grouped
    assert grouped["AWS"][0].configType == "topicPolicyConfig"

# Test for successful rollback when guardrail creation fails
def test_rollback_successful_guardrails_on_failure(guardrail_provider_map, create_guardrails_response, successful_providers):
    manager = GuardrailProviderManager()

    manager._rollback_successful_guardrails(create_guardrails_response, successful_providers, guardrail_provider_map)

    # Verify that delete_guardrail is called only on successful providers
    guardrail_provider_map['aws'].delete_guardrail.assert_called_once_with({"success": True})
    guardrail_provider_map['azure'].delete_guardrail.assert_called_once_with({"success": True})

# Test for no rollback when all guardrails are successful
def test_no_rollback_when_all_successful(guardrail_provider_map, create_guardrails_response, successful_providers):
    manager = GuardrailProviderManager()

    # Modify create_guardrails_response so that all are successful
    create_guardrails_response['gcp'] = {"success": True}
    successful_providers.append('gcp')

    manager._rollback_successful_guardrails(create_guardrails_response, successful_providers, guardrail_provider_map)

    # Ensure no rollback happens
    guardrail_provider_map['aws'].delete_guardrail.assert_not_called()
    guardrail_provider_map['gcp'].delete_guardrail.assert_not_called()
    guardrail_provider_map['azure'].delete_guardrail.assert_not_called()

# Test for missing guardrail response
def test_rollback_with_missing_response(guardrail_provider_map, create_guardrails_response, successful_providers):
    manager = GuardrailProviderManager()

    # Modify create_guardrails_response to have a missing entry
    del create_guardrails_response['azure']
    successful_providers.remove('azure')

    manager._rollback_successful_guardrails(create_guardrails_response, successful_providers, guardrail_provider_map)

    # Only 'aws' should be rolled back since 'azure' is missing from create_guardrails_response
    guardrail_provider_map['aws'].delete_guardrail.assert_called_once_with({"success": True})
    guardrail_provider_map['azure'].delete_guardrail.assert_not_called()

# Test when there are no successful providers to roll back
def test_no_rollback_when_no_successful_providers(guardrail_provider_map):
    manager = GuardrailProviderManager()

    create_guardrails_response = {
        'aws': {"success": False},
        'gcp': {"success": False},
        'azure': {"success": False}
    }
    successful_providers = []

    manager._rollback_successful_guardrails(create_guardrails_response, successful_providers, guardrail_provider_map)

    # No guardrails should be rolled back
    guardrail_provider_map['aws'].delete_guardrail.assert_not_called()
    guardrail_provider_map['gcp'].delete_guardrail.assert_not_called()
    guardrail_provider_map['azure'].delete_guardrail.assert_not_called()