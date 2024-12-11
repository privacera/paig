from typing import Optional

from pydantic import Field

from api.guardrails import GuardrailProvider
from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class GRSensitiveDataView(BaseView):
    """
    A model representing a GRSensitiveData.

    Attributes:
        name (str): The name of the sensitive data.
        label (str): The label of the sensitive data.
        guardrail_provider (GuardrailProvider): The guardrail's provider.
        description (Optional[str]): The description of the GRSensitiveData.
    """
    name: str = Field(default=None, description="The name of the sensitive data")
    label: str = Field(default=None, description="The label of the sensitive data")
    guardrail_provider: GuardrailProvider = Field(default=GuardrailProvider.PAIG, description="The guardrails provider", alias="guardrailsProvider")
    description: Optional[str] = Field(default=None, description="The Description of GRSensitiveData")

    model_config = BaseView.model_config


class GRSensitiveDataFilter(BaseAPIFilter):
    """
    A model representing a filter for GRSensitiveData.

    Attributes:
        id (int, optional): Filter by ID.
        name (str, optional): Filter by name.
        label (str, optional): Filter by label.
        guardrail_provider (GuardrailProvider): The guardrail's provider.
        description (str, optional): Filter by description.
    """

    name: Optional[str] = Field(default=None, description="The name of the sensitive data")
    label: Optional[str] = Field(default=None, description="The label of the sensitive data")
    guardrail_provider: Optional[GuardrailProvider] = Field(default=None, description="Filter by guardrails provider", alias="guardrailsProvider")
    description: Optional[str] = Field(default=None, description="The Description of GRSensitiveData")
