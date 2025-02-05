from pydantic import BaseModel, Field, Json
from typing import Literal, List, Optional, Any, Union, Dict

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter

class ConfigCommonModel(BaseModel):
    purpose: str = Field(..., max_length=1024)
    name: str = Field(..., max_length=1024)
    categories: list[Any]
    custom_prompts: list[Any]


class ConfigCreateRequest(ConfigCommonModel):
    application_ids: str

class ConfigUpdateRequest(ConfigCommonModel):
    application_ids: str


class EvalConfigFilter(BaseAPIFilter):
    """
    Filter class for AI application queries.

    Attributes:
        id (int, optional): Filter by ID.
        purpose (str, optional): Filter by purpose.
        name (str, optional): Filter by name.
    """

    id: Optional[int] = Field(default=None, description="Filter by id")
    purpose: Optional[str] = Field(default=None, description="Filter by purpose")
    name: Optional[str] = Field(default=None, description="Filter by name")

class EvalConfigView(BaseView):
    purpose: str = Field(..., max_length=1024)
    name: str = Field(..., max_length=1024)
    categories: str = Field(..., max_length=1024)
    custom_prompts: str = Field(..., max_length=1024)
    status: str = Field(..., max_length=1024)
    version: int = Field(..., gt=0)
    application_names: str
    eval_run_count: int
    owner: Optional[str] = Field(None, description="The User Name", alias="owner")
    model_config = BaseView.model_config
