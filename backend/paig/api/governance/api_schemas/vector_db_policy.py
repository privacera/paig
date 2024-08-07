from typing import Optional

from pydantic import Field

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class VectorDBPolicyView(BaseView):
    """
    A model representing an VectorDB policy.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the Vector DB policy.
        description (str): The description of the Vector DB policy.
        allowed_users (list[str]): The list of allowed users.
        allowed_groups (list[str]): The list of allowed groups.
        allowed_roles (list[str]): The list of allowed roles.
        denied_users (list[str]): The list of denied users.
        denied_groups (list[str]): The list of denied groups.
        denied_roles (list[str]): The list of denied roles.
        metadata_key (str): The metadata key for the policy.
        metadata_value (str): The metadata value for the policy.
        operator (str): The operator for the policy.
        vector_db_id (int): The vector db id for the policy.
    """
    name: Optional[str] = Field(default=None, description="The name of the Vector DB policy")
    description: Optional[str] = Field(default=None, description="The description of the Vector DB policy")

    allowed_users: list[str] = Field(default=[], description="The list of allowed users", alias="allowedUsers")
    allowed_groups: list[str] = Field(default=[], description="The list of allowed users", alias="allowedGroups")
    allowed_roles: list[str] = Field(default=[], description="The list of allowed users", alias="allowedRoles")

    denied_users: list[str] = Field(default=[], description="The list of denied users", alias="deniedUsers")
    denied_groups: list[str] = Field(default=[], description="The list of denied users", alias="deniedGroups")
    denied_roles: list[str] = Field(default=[], description="The list of denied users", alias="deniedRoles")

    metadata_key: str = Field(default=None, description="The metadata key for the policy", alias="metadataKey")
    metadata_value: str = Field(default=None, description="The metadata value for the policy", alias="metadataValue")
    operator: str = Field(default=None, description="The operator for the policy")
    vector_db_id: int = Field(default=None, description="The vector db id for the policy", alias="vectorDBId")

    class Config(BaseView.Config):
        pass


class VectorDBPolicyFilter(BaseAPIFilter):
    """
    Filter class for Vector DB policy queries.

    Attributes:
        name (str, optional): Filter by name.
        description (str, optional): Filter by description.
        user (str, optional): Filter by user.
        group (str, optional): Filter by group.
        role (str, optional): Filter by role.
        metadata_key (str, optional): Filter by metadata key.
        metadata_value (str, optional): Filter by metadata value.
        operator (str, optional): Filter by operator.
        vector_db_id (int, optional): Filter by vector db id.
    """

    name: Optional[str] = Field(default=None, description="Filter by name")
    description: Optional[str] = Field(default=None, description="Filter by description")

    user: Optional[str] = Field(default=None, description="Filter by user", json_schema_extra={"lookup_columns": ["allowed_users", "denied_users"]})
    group: Optional[str] = Field(default=None, description="Filter by group", json_schema_extra={"lookup_columns": ["allowed_groups", "denied_groups"]})
    role: Optional[str] = Field(default=None, description="Filter by role", json_schema_extra={"lookup_columns": ["allowed_roles", "denied_roles"]})

    metadata_key: Optional[str] = Field(default=None, description="Filter by metadata key", alias="metadataKey")
    metadata_value: Optional[str] = Field(default=None, description="Filter by metadata value", alias="metadataValue")
    operator: Optional[str] = Field(default=None, description="Filter by operator")
    vector_db_id: Optional[int] = Field(default=None, description="Filter by vector db id", alias="vectorDBId")
