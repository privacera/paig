from enum import Enum

from sqlalchemy import Column, String, Enum as SQLEnum
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel


class MetadataType(Enum):
    SYSTEM_DEFINED = 'SYSTEM_DEFINED'
    USER_DEFINED = 'USER_DEFINED'


class ValueDataType(Enum):
    MULTI_VALUE = 'multi_value'


class VectorDBMetaDataKeyModel(BaseSQLModel):
    """
    SQLAlchemy model representing Metadata.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the Metadata.
        status (int): Status of the Metadata.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        name (str): Name of the Metadata.
        type (MetadataType): Type of the Metadata.
        description (str): Description of Metadata.
        data_type (str): Datatype of Metadata.
    """

    __tablename__ = "vector_db_metadata_key"

    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(MetadataType), nullable=False)
    description = Column(String(4000), nullable=True)
    data_type = Column(String(255), nullable=False)

    metadata_values = relationship("VectorDBMetaDataValueModel", back_populates="metadata_key", cascade="all, delete-orphan")
