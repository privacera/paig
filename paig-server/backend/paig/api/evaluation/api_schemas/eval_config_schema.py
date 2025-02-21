from fastapi import Query
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
