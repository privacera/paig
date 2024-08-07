from typing import Optional, List

from pydantic import Field

from core.factory.database_initiator import BaseAPIFilter
from core.api_schemas.base_view import BaseView

from api.governance.database.db_models.vector_db_model import VectorDBType


class VectorDBView(BaseView):
    """
    A model representing an VectorDB.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the Vector DB.
        description (str): The description of the Vector DB.
        type (VectorDBType): The type of the Vector DB.
        user_enforcement (int): The user enforcement of the Vector DB.
        group_enforcement (int): The group enforcement of the Vector DB.
        ai_applications (Optional[str]): The AI applications associated with the Vector DB.
        
    """
    name: str = Field(default=None, description="The name of the Vector DB")
    description: str = Field(default=None, description="The description of the Vector DB")
    type: VectorDBType = Field(description="The type of the Vector DB")
    user_enforcement: int = Field(default=0, description="The user enforcement of the Vector DB", alias="userEnforcement")
    group_enforcement: int = Field(default=0, description="The group enforcement of the Vector DB", alias="groupEnforcement")
    ai_applications: Optional[List[str]] = Field(default=[],
                                                 description="The AI applications associated with the Vector DB",
                                                 alias="aiApplications")

    class Config(BaseView.Config):
        pass


class VectorDBFilter(BaseAPIFilter):
    """
    Filter class for Vector DB queries.

    Attributes:
        id (int, optional): Filter by ID.
        name (str, optional): Filter by name.
        type (str, optional): Filter by type.
        user_enforcement (int, optional): Filter by user enforcement.
        group_enforcement (int, optional): Filter by group enforcement.
    """

    name: Optional[str] = Field(default=None, description="Filter by name")
    type: Optional[VectorDBType] = Field(default=None, description="Filter by type")
    user_enforcement: Optional[int] = Field(default=None, description="Filter by user enforcement", alias="userEnforcement")
    group_enforcement: Optional[int] = Field(default=None, description="Filter by group enforcement", alias="groupEnforcement")
