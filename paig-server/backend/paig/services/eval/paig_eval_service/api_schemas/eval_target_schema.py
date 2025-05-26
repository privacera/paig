from enum import Enum
from fastapi import Query
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Any, Union, Dict
from core.factory.database_initiator import BaseAPIFilter


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class TargetCommonRequest(BaseModel):
    url: str = Field(..., min_length=1, description="The URL of the target")
    body: Union[Dict[str, Any], str] = Field(default="{}", description="body of target host")  # Accepts both dict & str
    headers: Union[Dict[str, Any], str] = Field(default="{}", description="headers of target host")  # Accepts both dict & str
    method: HttpMethod = Field(..., max_length=255, min_length=1, description="The method of the target")
    transformResponse: Optional[str] = Field(None, description="JS-like transform expression for the response")
    name: str = Field(..., max_length=255, min_length=1, pattern=r"^[^,]+$", description="The name of the target")
    username: Optional[str] = Field(None, description="The username of the target", pattern=r"^[^,]+$")


class TargetCreateRequest(TargetCommonRequest):
    ai_application_id: Optional[int] = Field(None, description="The AI application ID")


class TargetUpdateRequest(TargetCommonRequest):
    pass


class TargetTestRequest(BaseModel):
    url: HttpUrl = Field(..., description="Target URL to test")
    body: Optional[Union[Dict[str, Any], str]] = Field(default_factory=dict, description="Request body for the target")
    headers: Optional[Union[Dict[str, str], str]] = Field(default_factory=dict, description="Headers for the request")
    method: HttpMethod = Field(..., description="HTTP method to use")
    transformResponse: Optional[str] = Field(None, description="JS-like transform expression for the response")
    name: Optional[str] = Field(None, max_length=255, min_length=1, pattern=r"^[^,]+$", description="The name of the target")
    username: Optional[str] = Field(None, pattern=r"^[^,]+$", description="The username to associate with the target")
    ai_application_id: Optional[int] = Field(None, description="The AI application ID")


class QueryParamsBase(BaseAPIFilter):
    name: Optional[str] = Field(None, description="Name of application")


class IncludeQueryParams(QueryParamsBase):
    pass


def include_query_params(
        include_query_name: Optional[str] = Query(None, alias="includeQuery.name"),
) -> IncludeQueryParams:
    return IncludeQueryParams(
        name=include_query_name,
    )


def exclude_query_params(
        exclude_query_name: Optional[str] = Query(None, alias="excludeQuery.name"),
) -> QueryParamsBase:
    return QueryParamsBase(
        name=exclude_query_name,
    )


def extract_include_query_params(params):
    params_dict = params.model_dump(exclude=BaseAPIFilter.model_fields.keys(), by_alias=False, exclude_none=True)

    # Extract only the required fields
    filtered_params = {params.model_fields[field].alias: value for field, value in params_dict.items() if
                       value is not None}

    return filtered_params
