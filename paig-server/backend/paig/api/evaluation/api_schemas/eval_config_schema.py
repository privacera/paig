from fastapi import Query
from pydantic import BaseModel, Field
from typing import List, Optional

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter

class ConfigCommonModel(BaseModel):
    purpose: str = Field(..., description="The purpose of the config")
    name: str = Field(..., max_length=1024)
    categories: List[str] = Field(default_factory=[], description="The categories of evaluation")
    custom_prompts: List[str] = Field(default_factory=[], description="Custom prompts for evaluation")


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
    purpose: str = Field(..., description="The purpose of the config")
    name: str = Field(..., max_length=1024, description="The name of the config")
    categories: str = Field(..., description="The categories of evaluation")
    custom_prompts: str = Field(..., description="Custom prompts for evaluation")
    status: str = Field(..., max_length=1024, description="The status of the config")
    version: int = Field(..., gt=0, description="The version of the config")
    application_names: str = Field(..., description="The application names")
    eval_run_count: int = Field(..., ge=0, description="The number of evaluation runs")
    owner: Optional[str] = Field(None, description="The User Name", alias="owner")
    model_config = BaseView.model_config


class QueryParamsBase(BaseAPIFilter):
    purpose: Optional[str] = Field(None, description="purpose", alias="purpose")
    name: Optional[str] = Field(None, description="The Config name", alias="name")
    owner: Optional[str] = Field(None, description="The User ID", alias="owner")
    application_names: Optional[str] = Field(None, description="The Application name", alias="application_names")



class IncludeQueryParams(QueryParamsBase):
    pass

def include_query_params(
        include_query_application_names: Optional[str] = Query(None, alias="includeQuery.application_names"),
        include_query_purpose: Optional[str] = Query(None, alias="includeQuery.purpose"),
        include_query_name: Optional[str] = Query(None, alias="includeQuery.name"),
        include_query_owner: Optional[str] = Query(None, alias="includeQuery.owner"),
) -> IncludeQueryParams:
    return IncludeQueryParams(
        application_names=include_query_application_names,
        purpose=include_query_purpose,
        name=include_query_name,
        owner=include_query_owner
    )


def exclude_query_params(
        exclude_query_application_names: Optional[str] = Query(None, alias="excludeQuery.application_names"),
        exclude_query_purpose: Optional[str] = Query(None, alias="excludeQuery.purpose"),
        exclude_query_name: Optional[str] = Query(None, alias="excludeQuery.name"),
        exclude_query_owner: Optional[str] = Query(None, alias="excludeQuery.owner"),
) -> QueryParamsBase:
    return QueryParamsBase(
        application_names=exclude_query_application_names,
        purpose=exclude_query_purpose,
        name=exclude_query_name,
        owner=exclude_query_owner
    )


def extract_include_query_params(params):
    params_dict = params.model_dump(exclude=BaseAPIFilter.model_fields.keys(), by_alias=False, exclude_none=True)

    # Extract only the required fields
    filtered_params = {params.model_fields[field].alias: value for field, value in params_dict.items() if
                       value is not None}

    return filtered_params
