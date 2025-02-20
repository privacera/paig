
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList


class AIApplicationModel(BaseSQLModel):
    """
    SQLAlchemy model representing AI applications.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the AI application.
        status (int): Status of the AI application.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        name (str): Name of the AI application.
        description (str): Description of the AI application.
        application_key (str): Key for the AI application.
        vector_dbs (list): List of vector databases associated with the AI application.
    """

    __tablename__ = "ai_application"

    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    application_key = Column(String(255), nullable=False)
    vector_dbs = Column(CommaSeparatedList(255), nullable=True)
    guardrail_details = Column(String(255), nullable=True)
    guardrails = Column(CommaSeparatedList(255), nullable=True)

    app_config = relationship("AIApplicationConfigModel", back_populates="ai_app", uselist=False, cascade="all, delete-orphan")
    app_policies = relationship("AIApplicationPolicyModel", back_populates="ai_app", cascade="all, delete-orphan")
