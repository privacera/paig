from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel


class AIApplicationEncryptionKeyModel(BaseSQLModel):
    """
    SQLAlchemy model representing AI application encryption keys.

    Attributes:
        __tablename__ (str): Name of the database table.
        key (str): Encryption key
        application_id (int): The application ID.
    """

    __tablename__ = "ai_application_encryption_key"

    key = Column(String(255), nullable=False)
    application_id = Column(Integer, ForeignKey('ai_application.id', ondelete='CASCADE', name='fk_ai_application_policy_application_id'), nullable=False)


class AIApplicationAPIKeyModel(BaseSQLModel):
    """
    SQLAlchemy model representing AI application API keys.
    scope: 1 - All access, 0 - No access
    api_key: API key
    expiry_time: Expiry time of the API key
    application_id: The AI application ID.
    """
    __tablename__ = "ai_application_api_key"
    scope = Column(Integer, nullable=False, default=1)
    api_key = Column(String(255), nullable=False)
    expiry_time = Column(DateTime, index=True, nullable=True)
    application_id = Column(Integer, ForeignKey('ai_application.id', ondelete='CASCADE', name='fk_ai_application_policy_application_id'), nullable=False)

