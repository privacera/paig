
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList
from core.utils import current_utc_time


class GuardrailModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrail table.

    Attributes:
        name (str): The name of the guardrail.
        description (str): The description of the guardrail.
        version (str): The version of the guardrail.
    """

    __tablename__ = "guardrail"
    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    version = Column(String(255), nullable=False, default=1)

    gr_app = relationship("GRApplicationModel", back_populates="guardrail", cascade="all, delete-orphan")
    gr_config = relationship("GRConfigModel", back_populates="guardrail", cascade="all, delete-orphan")
    gr_response = relationship("GRProviderResponseModel", back_populates="guardrail", cascade="all, delete-orphan")


class GRApplicationModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrail_application table.

    Attributes:
        guardrail_id (int): The guardrail id.
        application_id (int): The application id.
    """
    __tablename__ = "guardrail_application"
    guardrail_id = Column(Integer, ForeignKey('guardrail.id', ondelete='CASCADE', name='fk_guardrail_application_guardrail_id'), nullable=False)
    application_id = Column(Integer, nullable=False)

    guardrail = relationship("GuardrailModel", back_populates="gr_app")


class GRConfigModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrails_config table.

    Attributes:
        guardrail_id (int): The guardrail id.
        guardrail_provider (str): The guardrail provider.
        config_type (str): The config type.
        config_data (dict): The config data JSON.
    """
    __tablename__ = "guardrail_config"
    guardrail_id = Column(Integer, ForeignKey('guardrail.id', ondelete='CASCADE', name='fk_guardrail_config_guardrail_id'), nullable=False)
    guardrail_provider = Column(String(255), nullable=False)
    guardrail_provider_connection_name = Column(String(255), nullable=True)
    config_type = Column(String(255), nullable=False)
    config_data = Column(JSON, nullable=False)

    guardrail = relationship("GuardrailModel", back_populates="gr_config")


class GRProviderResponseModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrail_response table by creating/updating guardrails in end service.

    Attributes:
        guardrail_id (int): The guardrail id.
        guardrail_provider (str): The guardrail provider.
        response_data (dict): The guardrail response data JSON.
    """
    __tablename__ = "guardrail_provider_response"
    guardrail_id = Column(Integer, ForeignKey('guardrail.id', ondelete='CASCADE', name='fk_guardrail_provider_response_guardrail_id'), nullable=False)
    guardrail_provider = Column(String(255), nullable=False)
    response_data = Column(JSON, nullable=False)

    guardrail = relationship("GuardrailModel", back_populates="gr_response")


class GuardrailViewModel(BaseSQLModel):
    """
    SQLAlchemy model representing the paig_guardrail_view view.

    Attributes:
        name (str): The name of the guardrail.
        description (str): The description of the guardrail.
        version (str): The version of the guardrail.
        guardrail_provider (str): The guardrail provider.
        config_type (str): The config type.
        config_data (dict): The config data JSON.
        guardrail_provider_connection_name (str): The guardrail provider connection name.
        guardrail_connection (dict): The guardrail connection JSON.
        guardrail_provider_response (dict): The guardrail response JSON.
        application_ids (str): The application ids.
    """
    __tablename__ = "paig_guardrail_view"
    # id = Column(Integer, nullable=False)
    # status = Column(Integer, nullable=False, default=1)
    # create_time = Column(DateTime, nullable=False)
    # update_time = Column(DateTime, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(4000), nullable=True)
    version = Column(String(255), nullable=False, default=1)
    guardrail_provider = Column(String(255), nullable=False)
    guardrail_id = Column(Integer, nullable=False)
    config_type = Column(String(255), nullable=False)
    config_data = Column(JSON, nullable=False)
    guardrail_provider_connection_name = Column(String(255), nullable=True)
    guardrail_connection = Column(JSON, nullable=False)
    guardrail_provider_response = Column(JSON, nullable=False)
    application_ids = Column(CommaSeparatedList(255), nullable=False)
