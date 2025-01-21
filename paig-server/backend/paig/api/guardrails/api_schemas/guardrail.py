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
        config_data (Dict): The guardrail details.
        response_message (str): The response message.
    """
    config_type: GuardrailConfigType = Field(..., description="The guardrail config type", alias="configType")
    config_data: Dict = Field(..., description="The guardrail details", alias="configData")
    response_message: str = Field(..., description="The response message", alias="responseMessage")


class GuardrailView(BaseView):
    """
    A model representing the Guardrail.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the Guardrail.
        description (str): The description of the Guardrail.
        version (int): The version of the Guardrail.
        guardrail_provider (GuardrailProvider): The guardrail provider.
        guardrail_connection_name (str): The connection name to guardrail provider.
        application_keys (List[str]): The associated application keys.
        guardrail_configs (List[Dict]): The guardrail details.
        guardrail_provider_response (dict): The guardrail response info.
        guardrail_connection_details (dict): The guardrail connection details.
    """
    name: str = Field(default=None, description="The name of the Guardrail")
    description: Optional[str] = Field(default=None, description="The description of the Guardrail")
    version: Optional[int] = Field(default=1, description="The version of the Guardrail")
    guardrail_provider: Optional[GuardrailProvider] = Field(None, description="The guardrail provider", alias="guardrailProvider")
    guardrail_connection_name: Optional[str] = Field(None, description="The connection name to guardrail provider", alias="guardrailConnectionName")
    application_keys: Optional[List[str]] = Field(None, description="The associated application keys",
                                        alias="applicationKeys")
    guardrail_applications: Optional[List[GRApplicationView]] = Field(None, description="The guardrail applications",
                                                                      alias="guardrailApplications")
    guardrail_configs: Optional[List[GRConfigView]] = Field(None, description="The guardrail details",
                                                            alias="guardrailConfigs")
    guardrail_provider_response: Optional[Dict] = Field(None, description="The guardrail response info",
                                                        alias="guardrailProviderResponse")
    guardrail_connection_details: Optional[Dict] = Field(None, description="The guardrail connection details",
                                                         alias="guardrailConnectionDetails")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra='allow'
    )


class GuardrailsDataView(BaseView):
    """
    A model representing the Guardrails data, this is used to return as response for the shield request.
    This holds version, application key and list of guardrails.

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
        guardrail_provider (GuardrailProvider, optional): Filter by guardrail provider.
        guardrail_connection_name (str, optional): Filter by connection name.
        application_keys (List[str], optional): Filter by application keys.
    """
    name: Optional[str] = Field(default=None, description="Filter by name")
    description: Optional[str] = Field(default=None, description="Filter by description")
    version: Optional[int] = Field(default=None, description="Filter by version")
    guardrail_provider: Optional[GuardrailProvider] = Field(default=None, description="Filter by guardrail provider", alias="guardrailProvider")
    guardrail_connection_name: Optional[str] = Field(default=None, description="Filter by connection name", alias="guardrailConnectionName")
    application_keys: Optional[str] = Field(default=None, description="Filter by application keys", alias="applicationKey")
