import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.guardrails.database.db_models.gr_sensitive_data_model import GRSensitiveDataModel
from core.db_models.BaseSQLModel import BaseSQLModel
from api.guardrails import GuardrailProvider


# Mocking SQLAlchemy session for testing purposes
@pytest.fixture
def mock_sqlalchemy_session():
    engine = create_engine("sqlite:///:memory:")
    BaseSQLModel.metadata.create_all(engine)
    my_session = sessionmaker(bind=engine)
    session = my_session()
    yield session
    session.close()


def test_gr_sensitive_data_model_init():
    gr_sensitive_data_model = GRSensitiveDataModel()
    assert gr_sensitive_data_model


def test_gr_sensitive_data_model_attributes(mock_sqlalchemy_session):
    name = "Name"
    label = "NAME"
    guardrail_provider = GuardrailProvider.AWS  # Assuming AWS is a valid Enum value
    description = "Name of the person"

    gr_sensitive_data_model = GRSensitiveDataModel(
        name=name,
        label=label,
        guardrail_provider=guardrail_provider,
        description=description,
    )

    assert gr_sensitive_data_model.name == name
    assert gr_sensitive_data_model.label == label
    assert gr_sensitive_data_model.guardrail_provider == guardrail_provider
    assert gr_sensitive_data_model.description == description

    # Test nullable constraints
    assert gr_sensitive_data_model.name is not None
    assert gr_sensitive_data_model.label is not None
    assert gr_sensitive_data_model.guardrail_provider is not None
    assert gr_sensitive_data_model.description is not None