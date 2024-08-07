
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList


class AIApplicationConfigModel(BaseSQLModel):
    """
    SQLAlchemy model representing AI application configurations.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the AI application configuration.
        status (int): Status of the AI application configuration.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        allowed_users (list): List of allowed users for the AI application.
        allowed_groups (list): List of allowed groups for the AI application.
        allowed_roles (list): List of allowed roles for the AI application.
        denied_users (list): List of denied users for the AI application.
        denied_groups (list): List of denied groups for the AI application.
        denied_roles (list): List of denied roles for the AI application.
        application_id (int): The application ID.
    """

    __tablename__ = "ai_application_config"

    allowed_users = Column(CommaSeparatedList(255), nullable=True)
    allowed_groups = Column(CommaSeparatedList(255), nullable=True)
    allowed_roles = Column(CommaSeparatedList(255), nullable=True)
    denied_users = Column(CommaSeparatedList(255), nullable=True)
    denied_groups = Column(CommaSeparatedList(255), nullable=True)
    denied_roles = Column(CommaSeparatedList(255), nullable=True)
    application_id = Column(Integer, ForeignKey('ai_application.id', ondelete='CASCADE', name='fk_ai_application_config_application_id'), nullable=False)

    ai_app = relationship("AIApplicationModel", back_populates="app_config")
