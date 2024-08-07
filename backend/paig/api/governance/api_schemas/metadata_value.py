from typing import Optional

from pydantic import Field

from core.factory.database_initiator import BaseAPIFilter
from core.api_schemas.base_view import BaseView


class MetadataValueView(BaseView):
    """
    A model representing a Metadata attribute.

    Inherits from:
        BaseView: The base model containing common fields.

    Attributes:
        metadata_id (int): The id of the Metadata.
        metadata_name (Optional[str]): The name of the Metadata.
        metadata_value (str): The type of the Metadata.
    """
    metadata_id: int = Field(default=None, description="The id of the Metadata", alias="metadataId")
    metadata_name: Optional[str] = Field(default=None, description="The name of the Metadata Key", alias="metadataName")
    metadata_value: str = Field(default=None, description="The value of the Metadata", alias="metadataValue")

    class Config(BaseView.Config):
        pass


class MetadataValueFilter(BaseAPIFilter):
    """
    Filter class for queries.

    Attributes:
        metadata_id (int, optional): Filter by Metadata ID.
        metadata_name (str, optional): Filter by Metadata key.
        metadata_value (str, optional): Filter by Metadata value.
    """
    metadata_id: Optional[int] = Field(default=None, description="The id of the Metadata", alias="metadataId")
    metadata_name: Optional[str] = Field(default=None, description="The name of the Metadata Key", alias="metadataName")
    metadata_value: Optional[str] = Field(default=None, description="The type of the Metadata", alias="metadataValue")
