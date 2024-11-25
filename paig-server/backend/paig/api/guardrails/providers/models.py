from typing import Any, List
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
    # TODO: variable names should be snake_case
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

class GuardrailRequest(BaseModel):
    """Model representing a request for guardrails.

        Attributes:
            name (str): The name of the guardrail.
            description (str): A brief description of the guardrail.
            connectionDetails (dict): Connection details for the provider.
            guardrailConfigs (List[GuardrailConfig]): A list of guardrail configurations.
        """
    name: str  # The name of the guardrail
    description: str
    connectionDetails: dict  # Connection details for the provider
    guardrailConfigs: List[GuardrailConfig]  # List of guardrail configurations

class CreateGuardrailRequest(GuardrailRequest):
    """Model representing a request to create guardrails.
    """
    pass

class UpdateGuardrailRequest(GuardrailRequest):
    """Model representing a request to update guardrails.

    Attributes:
        remoteGuardrailDetails (dict): Remote guardrail details.
    """
    remoteGuardrailDetails: dict # Remote guardrail details

class DeleteGuardrailRequest(GuardrailRequest):
    """Model representing a request to delete guardrails.

    Attributes:
        remoteGuardrailDetails (dict): Remote guardrail details.
    """
    remoteGuardrailDetails: dict # Remote guardrail details