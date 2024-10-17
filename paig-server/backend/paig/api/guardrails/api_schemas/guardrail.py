from typing import Optional, Dict, List

from pydantic import Field, ConfigDict

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class GuardrailConfigView(BaseView):
    """
    A model representing the Guardrail configuration.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        config_type (str): The guardrail type.
        guardrail_provider (str): The guardrail provider.
        config_data (Dict): The guardrail details.
    """
    guardrail_id: Optional[int] = Field(None, description="The guardrail id", alias="guardrailId")
    guardrail_provider: str = Field(..., description="The guardrail provider", alias="guardrailProvider")
    guardrail_provider_connection_name: Optional[str] = Field(None, description="The guardrail provider connection name", alias="guardrailProviderConnectionName")
    config_type: str = Field(..., description="The guardrail config type", alias="configType")
    config_data: Dict = Field(..., description="The guardrail details", alias="configData")

    model_config = ConfigDict()


class GuardrailView(BaseView):
    """
    A model representing the Guardrail.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the Guardrail.
        description (str): The description of the Guardrail.
        application_ids (int): The associated application ids.
        guardrail_configs (List[Dict]): The guardrail details.
        guardrail_provider_response (dict): The guardrail response info.
        guardrail_connections (dict): The guardrail connections.
    """
    name: str = Field(default=None, description="The name of the Guardrail")
    description: Optional[str] = Field(default=None, description="The description of the Guardrail")
    version: Optional[int] = Field(default=1, description="The version of the Guardrail")
    application_ids: List[int] = Field([], description="The associated application ids", alias="applicationIds")
    guardrail_configs: Optional[List[GuardrailConfigView]] = Field(None, description="The guardrail details",
                                                         alias="guardrailConfigs")
    guardrail_provider_response: Optional[Dict] = Field(None, description="The guardrail response info",
                                                        alias="guardrailProviderResponse")
    guardrail_connections: Optional[Dict] = Field(None, description="The guardrail connections",
                                                  alias="guardrailConnections")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class GuardrailFilter(BaseAPIFilter):
    """
    Filter class for Guardrails.

    Attributes:
        name (str, optional): Filter by name.
        description (str, optional): Filter by description.
        guardrail_provider (str, optional): Filter by guardrails' provider.
        connection_id (int, optional): Filter by connection id.
        guardrail_type (str, optional): Filter by guardrail type.
    """
    name: Optional[str] = Field(default=None, description="Filter by name")
    description: Optional[str] = Field(default=None, description="Filter by description")
    guardrail_provider: Optional[str] = Field(default=None, description="Filter by guardrails provider")
    connection_id: Optional[int] = Field(default=None, description="Filter by connection id")
    guardrail_type: Optional[str] = Field(default=None, description="Filter by guardrail type")
