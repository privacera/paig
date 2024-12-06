from sqlalchemy import Column, String, Integer, JSON

from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList


class GuardrailViewModel(BaseSQLModel):
    """
    SQLAlchemy model representing the paig_guardrail_view view.

    Attributes:
        name (str): The name of the guardrail.
        description (str): The description of the guardrail.
        version (str): The version of the guardrail.
        guardrail_provider (str): The guardrail provider.
        guardrail_id (int): The guardrail id.
        config_type (str): The config type.
        config_data (dict): The config data JSON.
        response_message (str): The response message.
    """
    __tablename__ = "paig_guardrail_view"

    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    version = Column(Integer, nullable=False, default=1)
    application_keys = Column(CommaSeparatedList(4000), nullable=False)

    guardrail_provider = Column(String(255), nullable=False)
    guardrail_id = Column(Integer, nullable=False)
    config_type = Column(String(255), nullable=False)
    config_data = Column(JSON, nullable=False)
    response_message = Column(String(255), nullable=False)


class GRConnectionViewModel(BaseSQLModel):
    """
    SQLAlchemy model representing the paig_guardrail_connection_view view.

    Attributes:
        name (str): The name of the connection.
        description (str): The description of the connection.
        guardrail_provider (str): The guardrail provider.
        connection_details (dict): The connection details JSON.
        guardrail_id (int): The guardrail id.
    """
    __tablename__ = "paig_guardrail_connection_view"

    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    guardrail_provider = Column(String(255), nullable=False)
    connection_details = Column(JSON, nullable=False)
    guardrail_id = Column(Integer, nullable=False)
