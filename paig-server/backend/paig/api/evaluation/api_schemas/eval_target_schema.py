from pydantic import BaseModel, Field, Json
from typing import Literal, List, Optional, Any, Union, Dict


class TargetCommonRequest(BaseModel):
    url: str = Field(..., max_length=255, min_length=1)
    body: Union[Dict[str, Any], str] = Field(default="{}")  # Accepts both dict & str
    headers: Union[Dict[str, Any], str] = Field(default="{}")  # Accepts both dict & str
    method: str = Field(..., max_length=255, min_length=1)
    transformResponse: str = Field(..., max_length=255, min_length=1)

class TargetCreateRequest(TargetCommonRequest):
    pass

class TargetUpdateRequest(TargetCommonRequest):
    pass