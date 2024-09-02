from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel


class VectorDBMetaDataValueModel(BaseSQLModel):
    """
    SQLAlchemy model representing Metadata attributes.

    Attributes:
        __tablename__ (str): Name of the database table.
        metadata_id (str): The ID of the Metadata.
        metadata_value (str): The value of the Metadata attribute.
    """

    __tablename__ = "vector_db_metadata_value"

    metadata_id = Column(Integer, ForeignKey('vector_db_metadata_key.id', ondelete='CASCADE', name='fk_vector_db_metadata_value_metadata_key_id'), nullable=False)
    metadata_value = Column(String(255), nullable=False)

    metadata_key = relationship("VectorDBMetaDataKeyModel", back_populates="metadata_values")
