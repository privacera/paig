import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from core.db_models.BaseSQLModel import BaseSQLModel


# Mocking SQLAlchemy session for testing purposes
@pytest.fixture
def mock_sqlalchemy_session():
    engine = create_engine('sqlite:///:memory:')
    BaseSQLModel.metadata.create_all(engine)
    my_session = sessionmaker(bind=engine)
    session = my_session()
    yield session
    session.close()


def test_guardrail_connection_model_init():
    guardrail_connection_model = GRConnectionModel()
    assert guardrail_connection_model


def test_guardrail_connection_model_attributes(mock_sqlalchemy_session):
    name = "mock_name"
    description = "mock_description"
    guardrail_provider = "mock_guardrail_provider"
    connection_details = {"mock_key": "mock_value"}

    guardrail_connection_model = GRConnectionModel(
        name=name,
        description=description,
        guardrail_provider=guardrail_provider,
        connection_details=connection_details
    )

    assert guardrail_connection_model.name == name
    assert guardrail_connection_model.description == description
    assert guardrail_connection_model.guardrail_provider == guardrail_provider
    assert guardrail_connection_model.connection_details == connection_details

    # Test nullable constraints
    assert guardrail_connection_model.name is not None
    assert guardrail_connection_model.description is not None
    assert guardrail_connection_model.guardrail_provider is not None
    assert guardrail_connection_model.connection_details is not None
