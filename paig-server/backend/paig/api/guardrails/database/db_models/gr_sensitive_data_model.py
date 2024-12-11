from sqlalchemy import Column, String, Enum as SQLEnum

from api.guardrails import GuardrailProvider
from core.db_models.BaseSQLModel import BaseSQLModel


class GRSensitiveDataModel(BaseSQLModel):
    """
    SQLAlchemy model representing GRSensitiveData.

    Attributes:
        __tablename__ (str): Name of the database table.
        id (int): Primary key identifier for the gr_sensitive_data.
        status (int): Status of the Metadata.
        create_time (datetime): Timestamp of creation.
        update_time (datetime): Timestamp of the last update.
        name (str): Name of the Guardrail Sensitive Data.
        label (str): Label of the Guardrail Sensitive Data.
        guardrail_provider (str): The guardrail provider.
        description (str): Description of gr_sensitive_data.
    """

    __tablename__ = "gr_sensitive_data"

    name = Column(String(255), nullable=False)
    label = Column(String(255), nullable=False)
    guardrail_provider = Column(SQLEnum(GuardrailProvider), nullable=False)
    description = Column(String(4000), nullable=True)
