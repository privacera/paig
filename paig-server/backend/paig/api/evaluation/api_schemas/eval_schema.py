import os
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, List, Optional
from core.factory.database_initiator import BaseAPIFilter
from fastapi import Query
from datetime import datetime


REPORT_URL = os.environ.get('REPORT_SERVER_BASE_URL', 'http://localhost:15500')

class GetCategories(BaseModel):
    purpose: str = Field(..., max_length=1024)

class BaseEvaluationView(BaseModel):
    application_names: str = Field(..., max_length=1024)
    config_name: str = Field(..., max_length=1024)
    purpose: str = Field(..., max_length=1024)
    eval_id: str = Field(..., max_length=1024)
    config_id: int
    status: str = Field(..., max_length=1024)
    owner: Optional[str] = Field(None, description="The User ID", alias="owner")
    passed: str
    failed: str
    id: int
    report_id: str
    create_time: Optional[datetime]
    report_url: str = Field(default=REPORT_URL)
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class QueryParamsBase(BaseAPIFilter):
    owner: Optional[str] = Field(None, description="The User ID", alias="owner")
    application_names: Optional[str] = Field(None, description="The Application name", alias="application_names")



class IncludeQueryParams(QueryParamsBase):
    pass

def include_query_params(
        include_query_application_names: Optional[str] = Query(None, alias="includeQuery.application_names"),
) -> IncludeQueryParams:
    return IncludeQueryParams(
        application_names=include_query_application_names,
    )


def exclude_query_params(
        exclude_query_application_names: Optional[str] = Query(None, alias="excludeQuery.application_names"),
) -> QueryParamsBase:
    return QueryParamsBase(
      application_names=exclude_query_application_names,
    )


def extract_include_query_params(params):
    params_dict = params.model_dump(exclude=BaseAPIFilter.model_fields.keys(), by_alias=False, exclude_none=True)

    # Extract only the required fields
    filtered_params = {params.model_fields[field].alias: value for field, value in params_dict.items() if
                       value is not None}

    return filtered_params