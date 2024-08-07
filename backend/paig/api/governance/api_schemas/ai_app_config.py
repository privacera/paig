from typing import Optional, List

from pydantic import Field

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class AIApplicationConfigView(BaseView):
    """
    A model representing the configuration of an AI application.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        allowed_users (List[str]): The allowed users for the AI application.
        allowed_groups (List[str]): The allowed groups for the AI application.
        allowed_roles (List[str]): The allowed roles for the AI application.
        denied_users (List[str]): The denied users for the AI application.
        denied_groups (List[str]): The denied groups for the AI application.
        denied_roles (List[str]): The denied roles for the AI application.
        application_id (int): The application ID.
    """

    allowed_users: Optional[List[str]] = Field([], description="The allowed users for the AI application",
                                               alias="allowedUsers")
    allowed_groups: Optional[List[str]] = Field([], description="The allowed groups for the AI application",
                                                alias="allowedGroups")
    allowed_roles: Optional[List[str]] = Field([], description="The allowed roles for the AI application",
                                               alias="allowedRoles")
    denied_users: Optional[List[str]] = Field([], description="The denied users for the AI application",
                                              alias="deniedUsers")
    denied_groups: Optional[List[str]] = Field([], description="The denied groups for the AI application",
                                               alias="deniedGroups")
    denied_roles: Optional[List[str]] = Field([], description="The denied roles for the AI application",
                                              alias="deniedRoles")
    application_id: Optional[int] = Field(None, description="The application ID", alias="applicationId")

    class Config:
        schema_extra = {
            "example": {
                "allowedUsers": ["user1", "user2"],
                "allowedGroups": ["group1", "group2"],
                "allowedRoles": ["role1", "role2"],
                "deniedUsers": ["user3", "user4"],
                "deniedGroups": ["group3", "group4"],
                "deniedRoles": ["role3", "role4"],
                "applicationId": 1
            }
        }


class AIApplicationConfigFilter(BaseAPIFilter):
    """
    Filter class for AI application configuration queries.

    Attributes:
        application_id (int, optional): Filter by application ID.
    """

    application_id: Optional[int] = Field(default=None, description="Filter by application ID")
    user: Optional[str] = Field(default=None, description="Filter by user", json_schema_extra={"lookup_columns": ["allowed_users", "denied_users"]})
    group: Optional[str] = Field(default=None, description="Filter by group", json_schema_extra={"lookup_columns": ["allowed_groups", "denied_groups"]})
    role: Optional[str] = Field(default=None, description="Filter by role", json_schema_extra={"lookup_columns": ["allowed_roles", "denied_roles"]})
