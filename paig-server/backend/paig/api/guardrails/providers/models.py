from typing import Any
from pydantic import BaseModel

# Define Enums for config types and guardrail providers
class GuardrailConfigType:
    """Enumeration of guardrail configuration types."""
    TOPIC_POLICY_CONFIG = "topicPolicyConfig"
    CONTENT_POLICY_CONFIG = "contentPolicyConfig"
    WORD_POLICY_CONFIG = "wordPolicyConfig"
    SENSITIVE_INFORMATION_POLICY_CONFIG = "sensitiveInformationPolicyConfig"
    CONTEXTUAL_GROUNDING_POLICY_CONFIG = "contextualGroundingPolicyConfig"
    BLOCKED_INPUTS_MESSAGING = "blockedInputMessaging"
    BLOCKED_OUTPUTS_MESSAGING = "blockedOutputsMessaging"


class GuardrailProviderType:
    """Enumeration of guardrail provider types."""
    AWS = "AWS"


class GuardrailConfig(BaseModel):
    """Model representing guardrail configuration.

    Attributes:
        status (int): The status of the guardrail configuration.
        guardrailProvider (str): The name of the guardrail provider.
        guardrailProviderConnectionName (str): The connection name for the guardrail provider.
        configType (str): The type of configuration being defined.
        configData (Any): The configuration data, which can vary in structure.
    """
    status: int  # Status as an integer
    guardrailProvider: str  # Guardrail provider
    guardrailProviderConnectionName: str  # Connection name as a string
    configType: str  # Configuration type
    configData: Any  # Configuration data as a dictionary


class GuardrailConnection(BaseModel):
    """Model representing a connection to a guardrail provider.

    Attributes:
        name (str): The name of the connection.
        description (str): A brief description of the connection.
        guardrailProvider (str): The name of the guardrail provider associated with the connection.
        connectionDetails (dict): A dictionary containing connection details for the provider.
    """
    name: str  # The name of the connection
    description: str  # A brief description of the connection
    guardrailProvider: str  # The name of the guardrail provider
    connectionDetails: dict  # Connection details for the provider
