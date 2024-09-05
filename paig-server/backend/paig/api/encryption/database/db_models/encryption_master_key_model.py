
from sqlalchemy import Column, String
from core.db_models.BaseSQLModel import BaseSQLModel


class EncryptionMasterKeyModel(BaseSQLModel):
    """
    SQLAlchemy model representing encryption keys.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the encryption key.
        status (int): Status of the AI encryption key.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        key (str): The master key.
    """

    __tablename__ = "encryption_master_key"

    key = Column(String, nullable=False)
