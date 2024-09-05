from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class BaseView(BaseModel):
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
    update_time: Optional[datetime] = Field(None, description="The last update time of the resource", alias="updateTime")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    @field_serializer('create_time', 'update_time')
    def serialize_timestamp(self, value: datetime) -> str:
        if value:
            return value.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
