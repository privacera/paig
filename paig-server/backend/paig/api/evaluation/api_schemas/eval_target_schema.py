from fastapi import Query
from pydantic import BaseModel, Field, Json
from typing import Literal, List, Optional, Any, Union, Dict
from core.factory.database_initiator import BaseAPIFilter

class TargetCommonRequest(BaseModel):
    url: str = Field(..., max_length=255, min_length=1)
    body: Union[Dict[str, Any], str] = Field(default="{}")  # Accepts both dict & str
    headers: Union[Dict[str, Any], str] = Field(default="{}")  # Accepts both dict & str
    method: str = Field(..., max_length=255, min_length=1)
    transformResponse: str = Field(..., max_length=255, min_length=1)
    name: str = Field(..., max_length=255, min_length=1)


class TargetCreateRequest(TargetCommonRequest):
    ai_application_id: Optional[int]

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