from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class EvaluationCommonModel(BaseModel):
    application_name: str = Field(..., max_length=1024)
    purpose: str = Field(..., max_length=1024)
    application_client: str = Field(..., max_length=1024)


class EvaluationConfigPlugins(EvaluationCommonModel):
    categories: List[str]
    static_prompts: List[dict]

