from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class BaseDataModel(BaseModel):
    """
    A base model for common fields shared across multiple models.

    Attributes:
        id (Optional[int]): The unique identifier of the resource.
        status (Optional[int]): The status of the resource.
        create_time (Optional[datetime]): The creation time of the resource.
        update_time (Optional[datetime]): The last update time of the resource.
    """
    id: Optional[int] = Field(None, description="The unique identifier of the resource")
    status: Optional[int] = Field(None, description="The status of the resource")
    create_time: Optional[datetime] = Field(None, description="The creation time of the resource", alias="createTime")
    update_time: Optional[datetime] = Field(None, description="The last update time of the resource",
                                            alias="updateTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    @field_serializer('create_time', 'update_time')
    def serialize_timestamp(self, value: datetime) -> str:
        if value:
            return value.strftime('%Y-%m-%dT%H:%M:%S.%f%z')


class AIApplicationData(BaseDataModel):
    """
    A model representing an AI application.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the AI application.
        description (str): The description of the AI application.
        application_key (str): The application key.

        vector_db_id (Optional[int]): The vector databases id with the AI application.
        vector_db_name (Optional[str]): The vector database associated with the AI application.
    """
    name: str = Field(default=None, description="The name of the AI application")
    description: Optional[str] = Field(default=None, description="The description of the AI application")
    application_key: Optional[str] = Field(None, description="The application key", alias="applicationKey")

    vector_db_id: Optional[int] = Field(None, description="The vector databases id with the AI application",
                                        alias="vectorDBId")
    vector_db_name: Optional[str] = Field(None, description="The vector database associated with the AI application",
                                          alias="vectorDBName")

    model_config = BaseDataModel.model_config


class AIApplicationConfigData(BaseDataModel):
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

    model_config = BaseDataModel.model_config


class AIApplicationPolicyData(BaseDataModel):
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
        prompt (str): The prompt associated with the AI application policy.
        reply (str): The reply associated with the AI application policy.
        enriched_prompt (str): The enriched prompt associated with the AI application policy.
        application_id (int): The application id associated with the AI application policy.
    """
    name: Optional[str] = Field("", description="The name of the AI application policy")
    description: str = Field(description="The description of the AI application policy")
    users: List[str] = Field(description="The users associated with the AI application policy")
    groups: List[str] = Field(description="The groups associated with the AI application policy")
    roles: List[str] = Field(description="The roles associated with the AI application policy")
    tags: List[str] = Field(description="The list of tags associated with the AI application policy",
                            alias="tags")
    prompt: str = Field(description="The prompt associated with the AI application policy")
    reply: str = Field(description="The reply associated with the AI application policy")
    enriched_prompt: str = Field(description="The enriched prompt associated with the AI application policy",
                                 alias="enrichedPrompt")
    application_id: int = Field(description="The application id associated with the AI application policy",
                                alias="applicationId", default=0)

    model_config = BaseDataModel.model_config


class VectorDBData(BaseDataModel):
    """
    A model representing an VectorDB.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the Vector DB.
        description (str): The description of the Vector DB.
        type (str): The type of the Vector DB.
        user_enforcement (int): The user enforcement of the Vector DB.
        group_enforcement (int): The group enforcement of the Vector DB.

    """
    name: str = Field(default=None, description="The name of the Vector DB")
    description: str = Field(default=None, description="The description of the Vector DB")
    type: str = Field(description="The type of the Vector DB")
    user_enforcement: int = Field(default=0, description="The user enforcement of the Vector DB",
                                  alias="userEnforcement")
    group_enforcement: int = Field(default=0, description="The group enforcement of the Vector DB",
                                   alias="groupEnforcement")

    model_config = BaseDataModel.model_config


class VectorDBPolicyData(BaseDataModel):
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

    model_config = BaseDataModel.model_config