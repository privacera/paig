from typing import Optional, Dict, List

from pydantic import Field, ConfigDict, BaseModel

from api.guardrails import GuardrailProvider, GuardrailConfigType
from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class GRConfigView(BaseModel):
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

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={GuardrailConfigType: lambda v: v.value}
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
        guardrail_provider (GuardrailProvider): The guardrail provider.
        guardrail_connection_name (str): The connection name to guardrail provider.
        guardrail_configs (List[Dict]): The guardrail details.
        guardrail_provider_response (dict): The guardrail response info.
        guardrail_connection_details (dict): The guardrail connection details.
    """
    name: str = Field(default=None, description="The name of the Guardrail")
    description: Optional[str] = Field(default=None, description="The description of the Guardrail")
    version: Optional[int] = Field(default=1, description="The version of the Guardrail")
    guardrail_provider: Optional[GuardrailProvider] = Field(None, description="The guardrail provider", alias="guardrailProvider")
    guardrail_connection_name: Optional[str] = Field(None, description="The connection name to guardrail provider", alias="guardrailConnectionName")
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


class GRVersionHistoryView(GuardrailView):
    """
    A model representing the Guardrail version history.

    Inherits from:
        GuardrailView: The model representing the Guardrail.

    Attributes:
        guardrail_id (int): The guardrail id.
    """
    guardrail_id: Optional[int] = Field(default=None, description="The guardrail id", alias="guardrailId")


class GuardrailFilter(BaseAPIFilter):
    """
    Filter class for Guardrails.

    Attributes:
        name (str, optional): Filter by name.
        description (str, optional): Filter by description.
        version (int, optional): Filter by version.
        guardrail_provider (GuardrailProvider, optional): Filter by guardrail provider.
        guardrail_connection_name (str, optional): Filter by connection name.
        extended (bool, optional): Include extended information.
        tenant_id (str, optional): The tenant id.
    """
    name: Optional[str] = Field(default=None, description="Filter by name")
    description: Optional[str] = Field(default=None, description="Filter by description")
    version: Optional[int] = Field(default=None, description="Filter by version")
    guardrail_provider: Optional[GuardrailProvider] = Field(default=None, description="Filter by guardrail provider", alias="guardrailProvider")
    guardrail_connection_name: Optional[str] = Field(default=None, description="Filter by connection name", alias="guardrailConnectionName")
    extended: Optional[bool] = Field(default=False, description="Give the extended result with connections and guardrail responses")
    tenant_id: Optional[str] = Field(default=None, description="The tenant id", alias="tenantId")


class GRVersionHistoryFilter(GuardrailFilter):
    """
    Filter class for Guardrails version history.

    Inherits from:
        GuardrailFilter: The filter class for Guardrails.

    Attributes:
        version (int, optional): Filter by version.
    """
    guardrail_id: Optional[int] = Field(default=None, description="Filter by guardrail id", alias="guardrailId")
