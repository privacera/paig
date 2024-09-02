from enum import Enum

from sqlalchemy import Column, String, Enum as SQLEnum

from core.db_models.BaseSQLModel import BaseSQLModel


class TagType(Enum):
    SYSTEM_DEFINED = 'SYSTEM_DEFINED'
    USER_DEFINED = 'USER_DEFINED'


class TagModel(BaseSQLModel):
    """
    SQLAlchemy model representing Tag.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the tag.
        status (int): Status of the Metadata.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        name (str): Name of the Metadata.
        type (MetadataType): Type of the tag.
        description (str): Description of tag.
    """

    __tablename__ = "tag"

    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(TagType), nullable=False)
    description = Column(String(4000), nullable=True)
