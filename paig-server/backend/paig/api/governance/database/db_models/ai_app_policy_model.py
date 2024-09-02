from enum import Enum

from sqlalchemy import Column, Integer, String, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList


class PermissionType(Enum):
    ALLOW = 'ALLOW'
    DENY = 'DENY'
    REDACT = 'REDACT'


class AIApplicationPolicyModel(BaseSQLModel):
    """
    SQLAlchemy model representing AI application policies.

    Attributes:
        __tablename__ (str): Name of the database table.
        name (str): Name of the AI application policy.
        description (str): Description of the AI application policy.
        users (list): List of users associated with the AI application policy.
        groups (list): List of groups associated with the AI application policy.
        roles (list): List of roles associated with the AI application policy.
        tags (list): List of tags associated with the AI application policy.
        prompt (PermissionType): The prompt permission type.
        reply (PermissionType): The reply permission type.
        enriched_prompt (PermissionType): The enriched prompt permission type.
        application_id (int): The application ID.
    """

    __tablename__ = "ai_application_policy"

    name = Column(String(255), nullable=True)
    description = Column(String(4000), nullable=False)
    users = Column(CommaSeparatedList(1024), nullable=True)
    groups = Column(CommaSeparatedList(1024), nullable=True)
    roles = Column(CommaSeparatedList(1024), nullable=True)
    tags = Column(CommaSeparatedList(1024), nullable=True)
    prompt = Column(SQLEnum(PermissionType), nullable=True)
    reply = Column(SQLEnum(PermissionType), nullable=True)
    enriched_prompt = Column(SQLEnum(PermissionType), nullable=True)
    application_id = Column(Integer, ForeignKey('ai_application.id', ondelete='CASCADE', name='fk_ai_application_policy_application_id'), nullable=False)

    ai_app = relationship("AIApplicationModel", back_populates="app_policies")
