
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from api.guardrails import GuardrailProvider
from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList


class BaseGuardrailModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrail table.

    Attributes:
        name (str): The name of the guardrail.
        description (str): The description of the guardrail.
        version (str): The version of the guardrail.
        guardrail_provider (str): The guardrail provider.
        guardrail_connection_name (str): The connection name to guardrail provider.
        guardrail_configs (List[Dict]): The guardrail details.
    """

    # __tablename__ = "guardrail"
    __abstract__ = True
    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    guardrail_provider = Column(SQLEnum(GuardrailProvider), nullable=True)
    guardrail_connection_name = Column(String(255), nullable=True)
    guardrail_configs = Column(JSON, nullable=False)
    guardrail_provider_response = Column(JSON, nullable=True)


class GuardrailModel(BaseGuardrailModel):
    """
    SQLAlchemy model representing the guardrail table.

    Attributes:
        gr_version_history (relationship): The guardrail history relationship.
    """
    __tablename__ = "guardrail"
    gr_version_history = relationship("GRVersionHistoryModel", back_populates="guardrail", cascade="all, delete-orphan")


class GRVersionHistoryModel(BaseGuardrailModel):
    """
    SQLAlchemy model representing the guardrail_version_history table.

    Attributes:
        guardrail_id (int): The guardrail id.
        version (int): The version of the guardrail.
        guardrail (relationship): The guardrail relationship.
    """

    __tablename__ = "guardrail_version_history"
    guardrail_id = Column(Integer, ForeignKey('guardrail.id', ondelete='CASCADE', name='fk_guardrail_version_history_guardrail_id'), nullable=False)
    version = Column(Integer, nullable=False, default=1)

    guardrail = relationship("GuardrailModel", back_populates="gr_version_history")
