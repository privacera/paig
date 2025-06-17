from enum import Enum
import json

from fastapi import Query
from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional, Any, Union, Dict
from core.factory.database_initiator import BaseAPIFilter
from core.utils import validate_url_format, validate_json_field


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class TargetCommonRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048, description="The URL of the target")
    body: Union[Dict[str, Any], str] = Field(default="{}", description="body of target host")  # Accepts both dict & str
    headers: Union[Dict[str, Any], str] = Field(default="{}", description="headers of target host")  # Accepts both dict & str
    method: HttpMethod = Field(..., max_length=255, min_length=1, description="The method of the target")
    transformResponse: str = Field(..., description="The transformResponse of the target")
    name: str = Field(..., max_length=255, min_length=1, pattern=r"^[^,]+$", description="The name of the target")
    username: Optional[str] = Field(None, description="The username of the target", pattern=r"^[^,]+$")

    @field_validator('url')
    @classmethod
    def validate_url_field(cls, v):
        return validate_url_format(v)

    @field_validator('headers')
    @classmethod
    def validate_headers_field(cls, v):
        return validate_json_field(v, "headers")

    @field_validator('body')
    @classmethod
    def validate_body_field(cls, v):
        return validate_json_field(v, "body")


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


class TargetApplicationConnectionRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048, description="The URL of the target")
    body: Union[Dict[str, Any], str] = Field(default="{}", description="body of target host")
    headers: Union[Dict[str, Any], str] = Field(default="{}", description="headers of target host")
    method: HttpMethod = Field(..., description="The method of the target")

    @field_validator('url')
    @classmethod
    def validate_url_field(cls, v):
        return validate_url_format(v)

    @field_validator('headers')
    @classmethod
    def validate_headers_field(cls, v):
        return validate_json_field(v, "headers")
    
    @field_validator('body')
    @classmethod
    def validate_body_field(cls, v):
        # First validate JSON structure
        validated_body = validate_json_field(v, "body")
        
        # Convert to string to check for prompt placeholder
        if isinstance(validated_body, dict):
            body_str = json.dumps(validated_body)
        else:
            body_str = str(validated_body)
        
        # Only replace {{prompt}} if it's present
        if "{{prompt}}" in body_str:
            test_body_str = body_str.replace("{{prompt}}", "Hello agent, this is a test input. No action required.")
            
            # Parse back to dict
            try:
                return json.loads(test_body_str)
            except json.JSONDecodeError:
                raise ValueError("body must be a valid JSON object after prompt replacement")
        
        return validated_body
