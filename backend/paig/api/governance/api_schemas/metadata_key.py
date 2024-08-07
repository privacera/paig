from typing import Optional

from pydantic import Field

from core.factory.database_initiator import BaseAPIFilter
from core.api_schemas.base_view import BaseView


class MetadataKeyView(BaseView):
    """
    A model representing a Metadata.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        name (str): The name of the Metadata.
        type (str): The type of the Metadata.
        description (Optional[str]): The description of the Metadata.
        data_type (str): The datatype of Metadata.
    """
    name: str = Field(default=None, description="The name of the Metadata")
    type: str = Field(default=None, description="The type of the Metadata")
    description: Optional[str] = Field(default=None, description="The Description of Metadata")
    data_type: str = Field(default=None, description="The datatype of Metadata", alias="valueDataType")

    class Config(BaseView.Config):
        pass


class MetadataKeyFilter(BaseAPIFilter):
    """
    Filter class for Metadata queries.

    Inherits from:
        BaseAPIFilter: The base model containing common fields.

    Attributes:
        name (Optional[str]): Filter by name.
        description (Optional[str]): Filter by description.
        data_type (Optional[str]): Filter by data type.
    """

    name: Optional[str] = Field(default=None, description="The name of the Metadata")
    description: Optional[str] = Field(default=None, description="The Description of Metadata")
    data_type: Optional[str] = Field(default=None, description="The datatype of Metadata", alias="valueDataType")
