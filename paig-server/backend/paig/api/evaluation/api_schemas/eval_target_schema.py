from enum import Enum

from fastapi import Query
from pydantic import BaseModel, Field
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
    transformResponse: str = Field(..., description="The transformResponse of the target")
    name: str = Field(..., max_length=255, min_length=1, description="The name of the target")


class TargetCreateRequest(TargetCommonRequest):
    ai_application_id: Optional[int] = Field(None, description="The AI application ID")

class TargetUpdateRequest(TargetCommonRequest):
    pass



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