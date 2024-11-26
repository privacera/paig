import pytest
from pydantic import ValidationError

from api.guardrails.providers.models import GuardrailConfigType, GuardrailProviderType, GuardrailConfig, \
    GuardrailConnection


# Unit tests for GuardrailConfigType and GuardrailProviderType
def test_guardrail_config_type_values():
    """Test that GuardrailConfigType enumeration contains expected values."""
    assert GuardrailConfigType.TOPIC_POLICY_CONFIG == "topicPolicyConfig"
    assert GuardrailConfigType.CONTENT_POLICY_CONFIG == "contentPolicyConfig"
    assert GuardrailConfigType.WORD_POLICY_CONFIG == "wordPolicyConfig"
    assert GuardrailConfigType.SENSITIVE_INFORMATION_POLICY_CONFIG == "sensitiveInformationPolicyConfig"
    assert GuardrailConfigType.CONTEXTUAL_GROUNDING_POLICY_CONFIG == "contextualGroundingPolicyConfig"
    assert GuardrailConfigType.BLOCKED_INPUTS_MESSAGING == "blockedInputMessaging"
    assert GuardrailConfigType.BLOCKED_OUTPUTS_MESSAGING == "blockedOutputsMessaging"


def test_guardrail_provider_type_values():
    """Test that GuardrailProviderType enumeration contains expected values."""
    assert GuardrailProviderType.AWS == "AWS"


# Unit tests for GuardrailConfig
def test_guardrail_config_valid_data():
    """Test that GuardrailConfig accepts valid data."""
    config_data = {"rules": ["rule1", "rule2"]}
    config = GuardrailConfig(
        guardrailProvider="AWS",
        configType=GuardrailConfigType.TOPIC_POLICY_CONFIG,
        configData=config_data
    )

    assert config.guardrailProvider == "AWS"
    assert config.configType == GuardrailConfigType.TOPIC_POLICY_CONFIG
    assert config.configData == config_data


def test_guardrail_config_invalid_data():
    """Test that GuardrailConfig raises a validation error with invalid data."""
    with pytest.raises(ValidationError):
        GuardrailConfig(
            guardrailProvider=123,  # Invalid value
            configType=GuardrailConfigType.TOPIC_POLICY_CONFIG,
            configData={"rules": ["rule1", "rule2"]}
        )


def test_guardrail_config_missing_required_fields():
    """Test that GuardrailConfig raises a validation error when required fields are missing."""
    with pytest.raises(ValidationError):
        GuardrailConfig(
            configType=GuardrailConfigType.TOPIC_POLICY_CONFIG,
            configData={"rules": ["rule1", "rule2"]}
        )


# Unit tests for GuardrailConnection
def test_guardrail_connection_valid_data():
    """Test that GuardrailConnection accepts valid data."""
    connection_details = {"access_key": "123", "secret_key": "abc"}
    connection = GuardrailConnection(
        name="MyConnection",
        description="A test connection",
        guardrailProvider="AWS",
        connectionDetails=connection_details
    )

    assert connection.name == "MyConnection"
    assert connection.description == "A test connection"
    assert connection.guardrailProvider == "AWS"
    assert connection.connectionDetails == connection_details


def test_guardrail_connection_invalid_data():
    """Test that GuardrailConnection raises a validation error with invalid data."""
    with pytest.raises(ValidationError):
        GuardrailConnection(
            name=123,  # Invalid type, should be str
            description="A test connection",
            guardrailProvider="AWS",
            connectionDetails={"access_key": "123", "secret_key": "abc"}
        )


def test_guardrail_connection_missing_required_fields():
    """Test that GuardrailConnection raises a validation error when required fields are missing."""
    with pytest.raises(ValidationError):
        GuardrailConnection(
            description="A test connection",
            guardrailProvider="AWS",
            connectionDetails={"access_key": "123", "secret_key": "abc"}
        )
