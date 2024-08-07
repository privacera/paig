from enum import Enum

from sqlalchemy import Column, String, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel


class VectorDBType(Enum):
    OPENSEARCH = 'OPENSEARCH'
    MILVUS = 'MILVUS'


class VectorDBModel(BaseSQLModel):
    """
    SQLAlchemy model representing Vector DB.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the Vector DB.
        status (int): Status of the Vector DB.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        name (str): Name of the Vector DB.
        description (str): Description of the Vector DB.
        type (VectorDBType): The type of the Vector DB.
    """

    __tablename__ = "vector_db"

    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    type = Column(SQLEnum(VectorDBType), nullable=True)
    user_enforcement = Column(Integer, nullable=False, default=0)
    group_enforcement = Column(Integer, nullable=False, default=0)

    vector_db_policies = relationship("VectorDBPolicyModel", back_populates="vector_db", cascade="all, delete-orphan")
