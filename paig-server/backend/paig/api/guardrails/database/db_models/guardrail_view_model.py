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
        guardrail_provider_connection_name (str): The guardrail provider connection name.
        guardrail_connection (dict): The guardrail connection JSON.
        guardrail_provider_response (dict): The guardrail response JSON.
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

    guardrail_provider_connection_name = Column(String(255), nullable=True)
    guardrail_connection = Column(JSON, nullable=False)
    guardrail_provider_response = Column(JSON, nullable=False)