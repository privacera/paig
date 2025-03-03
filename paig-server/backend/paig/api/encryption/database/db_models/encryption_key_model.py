from enum import Enum

from sqlalchemy import Column, String, Enum as SQLEnum
from core.db_models.BaseSQLModel import BaseSQLModel


class EncryptionKeyType(Enum):
    MSG_PROTECT_SHIELD = 'MSG_PROTECT_SHIELD'
    MSG_PROTECT_PLUGIN = 'MSG_PROTECT_PLUGIN'
    CRDS_PROTECT_GUARDRAIL = 'CRDS_PROTECT_GUARDRAIL'


class EncryptionKeyStatus(Enum):
    ACTIVE = 'ACTIVE'
    PASSIVE = 'PASSIVE'
    DISABLED = 'DISABLED'
    DELETED = 'DELETED'


class EncryptionKeyModel(BaseSQLModel):
    """
    SQLAlchemy model representing encryption keys.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the encryption key.
        status (int): Status of the AI encryption key.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        public_key (str): The public key.
        private_key (str): The private key.
        key_status (EncryptionKeyStatus): The status of the key.
        key_type (EncryptionKeyType): The type of the key.
    """

    __tablename__ = "encryption_key"

    public_key = Column(String, nullable=False)
    private_key = Column(String, nullable=False)
    key_status = Column(SQLEnum(EncryptionKeyStatus), nullable=False)
    key_type = Column(SQLEnum(EncryptionKeyType), nullable=False)
