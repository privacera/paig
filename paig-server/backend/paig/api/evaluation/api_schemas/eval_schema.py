from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from core.factory.database_initiator import BaseAPIFilter
from fastapi import Query
from datetime import datetime
from api.evaluation.api_schemas.eval_config_schema import ConfigCreateRequest


class GetCategories(BaseModel):
    purpose: str = Field(..., description="The purpose of the config")

class SaveAndRunRequest(ConfigCreateRequest):
    report_name: str = Field(..., max_length=1024, description="The name of the report")

class RunRequest(BaseModel):
    report_name: str = Field(..., max_length=1024, description="The name of the report")

class BaseEvaluationView(BaseModel):
    name: str = Field(..., max_length=1024, description="The name of the report")
    application_names: str = Field(..., max_length=1024, description="The application names")
    config_name: str = Field(..., max_length=1024, description="The config name")
    purpose: str = Field(..., description="The purpose of the config")
    eval_id: str = Field(..., max_length=1024, description="The eval id")
    config_id: int = Field(..., description="The config id")
    status: str = Field(..., max_length=1024, description="The status of the config")
    owner: Optional[str] = Field(None, description="The User ID", alias="owner")
    passed: str = Field(..., description="The number of passed evaluations")
    failed: str = Field(..., description="The number of failed evaluations")
    id: int = Field(..., description="The id of the evaluation")
    create_time: Optional[datetime] = Field(None, description="The create time of the evaluation")
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class QueryParamsBase(BaseAPIFilter):
    owner: Optional[str] = Field(None, description="The User ID", alias="owner")
    application_names: Optional[str] = Field(None, description="The Application name for the eval", alias="application_names")
    config_name: Optional[str] = Field(None, description="The Config name of eval", alias="config_name")
    purpose: Optional[str] = Field(None, description="The Purpose of eval", alias="purpose")
    name: Optional[str] = Field(None, description="The report name of eval", alias="name")
    status: Optional[str] = Field(None, description="The Status of eval", alias="status")



class IncludeQueryParams(QueryParamsBase):
    pass

def include_query_params(
        include_query_application_names: Optional[str] = Query(None, alias="includeQuery.application_names"),
        include_query_owner: Optional[str] = Query(None, alias="includeQuery.owner"),
        include_query_config_name: Optional[str] = Query(None, alias="includeQuery.config_name"),
        include_query_purpose: Optional[str] = Query(None, alias="includeQuery.purpose"),
        include_query_name: Optional[str] = Query(None, alias="includeQuery.name"),
        include_query_status: Optional[str] = Query(None, alias="includeQuery.status"),
) -> IncludeQueryParams:
    return IncludeQueryParams(
        application_names=include_query_application_names,
        owner=include_query_owner,
        config_name=include_query_config_name,
        purpose=include_query_purpose,
        name=include_query_name,
        status=include_query_status
    )


def exclude_query_params(
        exclude_query_application_names: Optional[str] = Query(None, alias="excludeQuery.application_names"),
        exclude_query_owner: Optional[str] = Query(None, alias="excludeQuery.owner"),
        exclude_query_config_name: Optional[str] = Query(None, alias="excludeQuery.config_name"),
        exclude_query_purpose: Optional[str] = Query(None, alias="excludeQuery.purpose"),
        exclude_query_name: Optional[str] = Query(None, alias="excludeQuery.name"),
        exclude_query_status: Optional[str] = Query(None, alias="excludeQuery.status"),
) -> QueryParamsBase:
    return QueryParamsBase(
        application_names=exclude_query_application_names,
        owner=exclude_query_owner,
        config_name=exclude_query_config_name,
        purpose=exclude_query_purpose,
        name=exclude_query_name,
        status=exclude_query_status
    )


def extract_include_query_params(params):
    params_dict = params.model_dump(exclude=BaseAPIFilter.model_fields.keys(), by_alias=False, exclude_none=True)

    # Extract only the required fields
    filtered_params = {params.model_fields[field].alias: value for field, value in params_dict.items() if
                       value is not None}

    return filtered_params


class ResultsQueryParamsBase(BaseAPIFilter):
    prompt: Optional[str] = Field(None, description="prompt", alias="prompt")
    response: Optional[str] = Field(None, description="response", alias="response")
    category: Optional[str] = Field(None, description="category", alias="category")
    status: Optional[str] = Field(None, description="status", alias="status")




class ResultsIncludeQueryParams(ResultsQueryParamsBase):
    pass


def results_include_query_params(
        include_query_prompt: Optional[str] = Query(None, alias="includeQuery.prompt"),
        include_query_response: Optional[str] = Query(None, alias="includeQuery.response"),
        include_query_category: Optional[str] = Query(None, alias="includeQuery.category"),
        include_query_status: Optional[str] = Query(None, alias="includeQuery.status"),
) -> ResultsIncludeQueryParams:
    return ResultsIncludeQueryParams(
        prompt=include_query_prompt,
        response=include_query_response,
        category=include_query_category,
        status=include_query_status
    )

def results_exclude_query_params(
        exclude_query_prompt: Optional[str] = Query(None, alias="excludeQuery.prompt"),
        exclude_query_response: Optional[str] = Query(None, alias="excludeQuery.response"),
        exclude_query_category: Optional[str] = Query(None, alias="excludeQuery.category"),
        exclude_query_status: Optional[str] = Query(None, alias="excludeQuery.status"),
) -> ResultsQueryParamsBase:
    return ResultsQueryParamsBase(
        prompt=exclude_query_prompt,
        response=exclude_query_response,
        category=exclude_query_category,
        status=exclude_query_status
    )