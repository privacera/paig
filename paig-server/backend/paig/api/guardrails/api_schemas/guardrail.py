from typing import Optional, Dict, List

from pydantic import Field, ConfigDict, BaseModel

from api.guardrails import GuardrailProvider, GuardrailConfigType
from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class GRApplicationView(BaseModel):
    """
    A model representing the Guardrail application.

    Attributes:
        application_key (str): The application key.
        application_id (int, optional): The application id.
        application_name (str): The application name.
    """
    application_key: Optional[str] = Field(..., description="The application key", alias="applicationKey")
    application_id: Optional[int] = Field(None, description="The application id", alias="applicationId")
    application_name: Optional[str] = Field(None, description="The application name", alias="applicationName")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class GRConfigView(BaseView):
    """
    A model representing the Guardrail configuration.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        config_type (str): The guardrail type.
        guardrail_provider (str): The guardrail provider.
        config_data (Dict): The guardrail details.
    """
    guardrail_provider: GuardrailProvider = Field(..., description="The guardrail provider", alias="guardrailProvider")
    config_type: GuardrailConfigType = Field(..., description="The guardrail config type", alias="configType")
    config_data: Dict = Field(..., description="The guardrail details", alias="configData")
    response_message: str = Field(..., description="The response message", alias="responseMessage")

    def to_guardrail_config(self):
        """
        Convert the Guardrails configuration view to a Guardrails configuration.

        Returns:
            GuardrailConfig: The Guardrails configuration.
        """
        from api.guardrails.providers import GuardrailConfig
        return GuardrailConfig(
            guardrailProvider=self.guardrail_provider,
            configType=self.config_type,
            configData=self.config_data
        )


class GuardrailView(BaseView):
    """
    A model representing the Guardrail.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the Guardrail.
        description (str): The description of the Guardrail.
        version (int): The version of the Guardrail.
        application_keys (List[str]): The associated application keys.
        guardrail_configs (List[Dict]): The guardrail details.
        guardrail_provider_response (dict): The guardrail response info.
        guardrail_connections (dict): The guardrail connections.
    """
    name: str = Field(default=None, description="The name of the Guardrail")
    description: Optional[str] = Field(default=None, description="The description of the Guardrail")
    version: Optional[int] = Field(default=1, description="The version of the Guardrail")
    enabled_providers: Optional[List[GuardrailProvider]] = Field(None, description="The enabled providers", alias="enabledProviders")
    application_keys: List[str] = Field(None, description="The associated application keys",
                                        alias="applicationKeys")
    guardrail_applications: Optional[List[GRApplicationView]] = Field(None, description="The guardrail applications",
                                                                      alias="guardrailApplications")
    guardrail_configs: Optional[List[GRConfigView]] = Field(None, description="The guardrail details",
                                                            alias="guardrailConfigs")
    guardrail_provider_response: Optional[Dict] = Field(None, description="The guardrail response info",
                                                        alias="guardrailProviderResponse")
    guardrail_connections: Dict = Field(..., description="The guardrail connections",
                                                  alias="guardrailConnections")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra='allow'
    )


class GuardrailsDataView(BaseView):
    """
    A model representing the Guardrails data.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        app_key (str): The application key.
        version (int): The version of the Guardrails.
        guardrails (List[GuardrailView]): The list of Guardrails.
    """
    app_key: str = Field(..., description="The application key", alias="applicationKey")
    version: int = Field(..., description="The version of the Guardrails")
    guardrails: Optional[List[GuardrailView]] = Field(None, description="The list of Guardrails")


class GuardrailFilter(BaseAPIFilter):
    """
    Filter class for Guardrails.

    Attributes:
        name (str, optional): Filter by name.
        description (str, optional): Filter by description.
        version (int, optional): Filter by version.
    """
    name: Optional[str] = Field(default=None, description="Filter by name")
    description: Optional[str] = Field(default=None, description="Filter by description")
    version: Optional[int] = Field(default=None, description="Filter by version")
    enabled_providers: Optional[List[str]] = Field(None, description="Filter by enabled providers", alias="enabledProviders")
