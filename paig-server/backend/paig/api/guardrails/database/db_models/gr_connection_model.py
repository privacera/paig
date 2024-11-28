from sqlalchemy import Column, String, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from api.guardrails import GuardrailProvider
from core.db_models.BaseSQLModel import BaseSQLModel


class GRConnectionModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrails_connection table.

    Attributes:
        name (str): The name of the connection.
        description (str): The description of the connection.
        guardrail_provider (str): The guardrail provider.
        connection_details (dict): The connection details JSON.
    """

    __tablename__ = "guardrail_connection"
    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    guardrail_provider = Column(SQLEnum(GuardrailProvider), nullable=False)
    connection_details = Column(JSON, nullable=False)

    gr_connection_mapping = relationship("GRConnectionMappingModel", back_populates="gr_connection")
