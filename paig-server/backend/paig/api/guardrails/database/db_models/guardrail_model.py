
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from api.guardrails import GuardrailProvider, GuardrailConfigType
from core.db_models.BaseSQLModel import BaseSQLModel
from core.db_models.utils import CommaSeparatedList


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
    version = Column(Integer, nullable=False, default=1)
    enabled_providers = Column(CommaSeparatedList(255), nullable=True)

    gr_application = relationship("GRApplicationModel", back_populates="guardrail", cascade="all, delete-orphan")
    gr_config = relationship("GRConfigModel", back_populates="guardrail", cascade="all, delete-orphan")
    gr_response = relationship("GRProviderResponseModel", back_populates="guardrail", cascade="all, delete-orphan")
    gr_connection_mapping = relationship("GRConnectionMappingModel", back_populates="guardrail", cascade="all, delete-orphan")


class GRConnectionMappingModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrails_connection table.

    Attributes:
        guardrail_id (int): The guardrail id.
        gr_connection_id (int): The guardrail connection id.
        guardrail_provider (str): The guardrail provider.
    """
    __tablename__ = "guardrail_connection_mapping"
    guardrail_id = Column(Integer, ForeignKey('guardrail.id', ondelete='CASCADE', name='fk_guardrail_connection_mapping_guardrail_id'), nullable=False)
    gr_connection_id = Column(Integer, ForeignKey('guardrail_connection.id', name='fk_guardrail_connection_mapping_gr_connection_id'), nullable=False)
    guardrail_provider = Column(SQLEnum(GuardrailProvider), nullable=False)

    guardrail = relationship("GuardrailModel", back_populates="gr_connection_mapping")
    gr_connection = relationship("GRConnectionModel", back_populates="gr_connection_mapping")


class GRApplicationModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrails_applications table.

    Attributes:
        guardrail_id (int): The guardrail id.
        application_id (int): The application id.
        application_name (str): The application name.
        application_key (str): The application key.
    """
    __tablename__ = "guardrail_application"
    guardrail_id = Column(Integer, ForeignKey('guardrail.id', ondelete='CASCADE', name='fk_guardrail_application_guardrail_id'), nullable=False)
    application_id = Column(Integer, nullable=True)
    application_name = Column(String(255), nullable=True)
    application_key = Column(String(255), nullable=False, index=True)

    guardrail = relationship("GuardrailModel", back_populates="gr_application")


class GRApplicationVersionModel(BaseSQLModel):
    """
    SQLAlchemy model representing the guardrails_applications table.

    Attributes:
        application_key (str): The application key.
        version (int): The version of the application.
    """
    __tablename__ = "guardrail_application_version"
    application_key = Column(String(255), nullable=False, index=True)
    version = Column(Integer, nullable=False)


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
    guardrail_provider = Column(SQLEnum(GuardrailProvider), nullable=False)
    config_type = Column(SQLEnum(GuardrailConfigType), nullable=False)
    config_data = Column(JSON, nullable=False)
    response_message = Column(String(4000), nullable=True)

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
    guardrail_provider = Column(SQLEnum(GuardrailProvider), nullable=False)
    response_data = Column(JSON, nullable=False)

    guardrail = relationship("GuardrailModel", back_populates="gr_response")
