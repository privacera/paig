from pydantic import BaseModel, Field
from typing import Literal, List, Optional
from core.factory.database_initiator import BaseAPIFilter


class GroupCommonModel(BaseModel):
    status: Optional[Literal[0, 1]] = Field(None, description="Status of the group")
    description: str = Field(..., max_length=1024)


class GroupCreateRequest(GroupCommonModel):
    name: str = Field(..., max_length=255, min_length=1)


class GroupUpdateRequest(GroupCommonModel):
    pass


class GroupMemberUpdateRequest(BaseModel):
    addUsers: List[str]
    delUsers: List[str]


class GetGroupsFilterRequest(BaseAPIFilter):
    """
    A model representing a filter for groups

    Attributes:
        name (Optional[str]): Name of the group
    """
    name: Optional[str] = Field(None, description="Name of the group")