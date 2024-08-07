from typing import Optional, List

from pydantic import Field

from core.factory.database_initiator import BaseAPIFilter
from api.governance.api_schemas.ai_app import BaseView
from api.governance.database.db_models.ai_app_policy_model import PermissionType


class AIApplicationPolicyView(BaseView):
    """
    A model representing an AI application policy.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the AI application policy.
        description (str): The description of the AI application policy.
        users (List[str]): The users associated with the AI application policy.
        groups (List[str]): The groups associated with the AI application policy.
        roles (List[str]): The roles associated with the AI application policy.
        tags (List[str]): The list of tags associated with the AI application policy.
        prompt (PermissionType): The prompt associated with the AI application policy.
        reply (PermissionType): The reply associated with the AI application policy.
        enriched_prompt (PermissionType): The enriched prompt associated with the AI application policy.
        application_id (int): The application id associated with the AI application policy.
    """
    name: Optional[str] = Field("", description="The name of the AI application policy")
    description: str = Field(description="The description of the AI application policy")
    users: List[str] = Field(description="The users associated with the AI application policy")
    groups: List[str] = Field(description="The groups associated with the AI application policy")
    roles: List[str] = Field(description="The roles associated with the AI application policy")
    tags: List[str] = Field(description="The list of tags associated with the AI application policy")
    prompt: PermissionType = Field(description="The prompt associated with the AI application policy")
    reply: PermissionType = Field(description="The reply associated with the AI application policy")
    enriched_prompt: PermissionType = Field(description="The enriched prompt associated with the AI application policy", alias="enrichedPrompt")
    application_id: int = Field(description="The application id associated with the AI application policy", alias="applicationId", default=0)

    class Config(BaseView.Config):
        pass


class AIApplicationPolicyFilter(BaseAPIFilter):
    """
    A model representing a filter for AI application policies.

    Attributes:
        name (Optional[str]): The name of the AI application policy.
        description (Optional[str]): The description of the AI application policy.
        users (Optional[List[str]]): The users associated with the AI application policy.
        groups (Optional[List[str]]): The groups associated with the AI application policy.
        roles (Optional[List[str]]): The roles associated with the AI application policy.
        tags (Optional[List[str]]): The list of tags associated with the AI application policy.
        prompt (Optional[PermissionType]): The prompt associated with the AI application policy.
        reply (Optional[PermissionType]): The reply associated with the AI application policy.
        enriched_prompt (Optional[PermissionType]): The enriched prompt associated with the AI application policy.
        application_id (Optional[int]): The application id associated with the AI application policy.
    """
    name: Optional[str] = Field(None, description="The name of the AI application policy")
    description: Optional[str] = Field(None, description="The description of the AI application policy")
    users: Optional[str] = Field(None, description="The users associated with the AI application policy", alias="user")
    groups: Optional[str] = Field(None, description="The groups associated with the AI application policy", alias="group")
    roles: Optional[str] = Field(None, description="The roles associated with the AI application policy", alias="role")
    tags: Optional[str] = Field(None, description="The list of tags associated with the AI application policy", alias="tag")
    prompt: Optional[PermissionType] = Field(None, description="The prompt associated with the AI application policy")
    reply: Optional[PermissionType] = Field(None, description="The reply associated with the AI application policy")
    enriched_prompt: Optional[PermissionType] = Field(None, description="The enriched prompt associated with the AI application policy", alias="enrichedPrompt")
    application_id: Optional[int] = Field(None, description="The application id associated with the AI application policy", alias="applicationId")
