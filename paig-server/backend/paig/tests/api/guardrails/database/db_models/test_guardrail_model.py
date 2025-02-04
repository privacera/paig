import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails import GuardrailProvider, GuardrailConfigType, model_to_dict
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRApplicationVersionModel, \
    GRVersionHistoryModel
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


def test_guardrail_model_init():
    guardrail_model = GuardrailModel()
    assert guardrail_model


def test_guardrail_model_attributes(mock_sqlalchemy_session):
    name = "mock_name"
    description = "mock_description"
    version = 1
    guardrail_connection_name = "mock_connection",
    response_message = "I couldn't respond to that message."
    config_type = GuardrailConfigType.CONTENT_MODERATION
    config_data = {"mock_key": "mock_value"}
    guardrail_configs = [{
        "config_type": config_type,
        "config_data": config_data,
        "response_message": response_message
    }]
    guardrail_provider_response = {
        "AWS": {"success": True, "response": {"mock_key": "mock_value"}}
    }
    application_keys = ["mock_app_key"]

    guardrail_model = GuardrailModel(
        name=name,
        description=description,
        version=version,
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name=guardrail_connection_name,
        guardrail_configs=guardrail_configs,
        guardrail_provider_response=guardrail_provider_response,
        application_keys=application_keys
    )

    assert guardrail_model.name == name
    assert guardrail_model.description == description
    assert guardrail_model.version == version
    assert guardrail_model.guardrail_provider == GuardrailProvider.AWS
    assert guardrail_model.guardrail_connection_name == guardrail_connection_name
    assert guardrail_model.application_keys == application_keys
    assert guardrail_model.guardrail_configs == guardrail_configs
    assert guardrail_model.guardrail_provider_response == guardrail_provider_response

    # Test nullable constraints
    assert guardrail_model.name is not None
    assert guardrail_model.description is not None
    assert guardrail_model.version is not None
    assert guardrail_model.guardrail_provider is not None
    assert guardrail_model.guardrail_connection_name is not None
    assert guardrail_model.application_keys is not None
    assert guardrail_model.guardrail_configs is not None
    assert guardrail_model.guardrail_provider_response is not None


def test_gr_version_history_model_init():
    gr_version_history_model = GRVersionHistoryModel()
    assert gr_version_history_model


def test_gr_version_history_model_attributes(mock_sqlalchemy_session):
    guardrail_id = 1
    gr_application_model = GRVersionHistoryModel(
        guardrail_id=guardrail_id,
        version=1
    )

    assert gr_application_model.guardrail_id == guardrail_id
    assert gr_application_model.version == 1

    # Test nullable constraints
    assert gr_application_model.guardrail_id is not None
    assert gr_application_model.version is not None


def test_guardrail_application_version_model_init():
    gr_application_version_model = GRApplicationVersionModel()
    assert gr_application_version_model


def test_guardrail_application_version_model_attributes(mock_sqlalchemy_session):
    application_key = "mock_application_key"
    version = 1

    gr_application_version_model = GRApplicationVersionModel(
        application_key=application_key,
        version=version
    )

    assert gr_application_version_model.application_key == application_key
    assert gr_application_version_model.version == version

    # Test nullable constraints
    assert gr_application_version_model.application_key is not None
    assert gr_application_version_model.version is not None


@pytest.fixture
def guardrail(mock_sqlalchemy_session):
    response_message = "I couldn't respond to that message."
    config_type = GuardrailConfigType.CONTENT_MODERATION.name
    config_data = {"mock_key": "mock_value"}
    guardrail_instance = GuardrailModel(
        name="mock_name",
        description="mock_description",
        version=1,
        guardrail_connection_name="mock_connection",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_configs=[{
            "config_type": config_type,
            "config_data": config_data,
            "response_message": response_message
        }],
        guardrail_provider_response={
            "AWS": {"success": True, "response": {"mock_key": "mock_value"}}
        },
        application_keys=["mock_app_key"]
    )
    mock_sqlalchemy_session.add(guardrail_instance)
    mock_sqlalchemy_session.commit()
    return guardrail_instance


@pytest.fixture
def guardrail_connection(mock_sqlalchemy_session):
    guardrail_connection_instance = GRConnectionModel(
        name="mock_connection",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"mock_key": "mock_value"}
    )

    mock_sqlalchemy_session.add(guardrail_connection_instance)
    mock_sqlalchemy_session.commit()
    return guardrail_connection_instance


@pytest.fixture
def guardrail_version_history(mock_sqlalchemy_session, guardrail):
    response_message = "I couldn't respond to that message."
    config_type = GuardrailConfigType.CONTENT_MODERATION.name
    config_data = {"mock_key": "mock_value"}
    guardrail_model_instance = GuardrailModel(
        name="mock_name",
        description="mock_description",
        version=1,
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection",
        guardrail_configs=[{
            "config_type": config_type,
            "config_data": config_data,
            "response_message": response_message
        }],
        guardrail_provider_response={
            "AWS": {"success": True, "response": {"mock_key": "mock_value"}}
        },
        application_keys=["mock_app_key"]
    )
    gr_version_history_instance = GRVersionHistoryModel(**model_to_dict(guardrail_model_instance))
    gr_version_history_instance.id = None
    gr_version_history_instance.create_time = guardrail.update_time
    gr_version_history_instance.guardrail_id = 1

    mock_sqlalchemy_session.add(gr_version_history_instance)
    mock_sqlalchemy_session.commit()
    return gr_version_history_instance


def test_guardrail_has_version_history(mock_sqlalchemy_session, guardrail, guardrail_version_history):
    # Retrieve the guardrail from the database
    guardrail_from_db = mock_sqlalchemy_session.query(GuardrailModel).filter_by(name="mock_name").one()

    # Assert that the guardrail has the configuration associated with it
    assert len(guardrail_from_db.gr_version_history) == 1
    assert guardrail_from_db.gr_version_history is not None
    assert guardrail_from_db.gr_version_history[0].guardrail_id == guardrail_from_db.id
    assert guardrail_from_db.gr_version_history[0].version == 1


def test_config_has_guardrail(mock_sqlalchemy_session, guardrail, guardrail_version_history):
    # Retrieve the configuration from the database
    gr_version_history = mock_sqlalchemy_session.query(GRVersionHistoryModel).filter_by(name="mock_name").one()

    # Assert that the configuration has the correct guardrail associated with it
    assert gr_version_history.guardrail is not None
    assert gr_version_history.guardrail.name == "mock_name"
    assert gr_version_history.guardrail.description == "mock_description"
    assert gr_version_history.guardrail.version == 1
    assert gr_version_history.guardrail.guardrail_provider == GuardrailProvider.AWS
    assert gr_version_history.guardrail.guardrail_connection_name == "mock_connection"
    assert gr_version_history.guardrail.guardrail_configs[0]["response_message"] == "I couldn't respond to that message."
    assert gr_version_history.guardrail.guardrail_configs[0]["config_type"] == GuardrailConfigType.CONTENT_MODERATION.name
    assert gr_version_history.guardrail.guardrail_configs[0]["config_data"] == {"mock_key": "mock_value"}
    assert gr_version_history.guardrail.guardrail_provider_response == {
        "AWS": {"success": True, "response": {"mock_key": "mock_value"}}
    }
