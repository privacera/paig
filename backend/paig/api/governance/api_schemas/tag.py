from typing import Optional

from pydantic import Field

from core.api_schemas.base_view import BaseView
from core.factory.database_initiator import BaseAPIFilter


class TagView(BaseView):
    """
    A model representing a Tag.

    Attributes:
        name (str): The name of the Tag.
        type (str): The type of the Tag.
        description (Optional[str]): The description of the Tag.
    """
    name: str = Field(default=None, description="The name of the Tag")
    type: str = Field(default=None, description="The type of the Tag")
    description: Optional[str] = Field(default=None, description="The Description of Tag")

    class Config(BaseView.Config):
        pass


class TagFilter(BaseAPIFilter):
    """
    A model representing a filter for Tag.

    Attributes:
        id (int, optional): Filter by ID.
        name (str, optional): Filter by name.
    """

    name: Optional[str] = Field(default=None, description="The name of the Tag")
    type: Optional[str] = Field(default=None, description="The type of the Tag")
    description: Optional[str] = Field(default=None, description="The Description of Tag")
