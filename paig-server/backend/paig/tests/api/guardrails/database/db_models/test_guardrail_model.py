import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails import GuardrailProvider, GuardrailConfigType
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, GRApplicationModel, \
    GRApplicationVersionModel, GRConfigModel, GRProviderResponseModel, GRConnectionMappingModel
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

    guardrail_model = GuardrailModel(
        name=name,
        description=description,
        version=version
    )

    assert guardrail_model.name == name
    assert guardrail_model.description == description
    assert guardrail_model.version == version

    # Test nullable constraints
    assert guardrail_model.name is not None
    assert guardrail_model.description is not None
    assert guardrail_model.version is not None


def test_gr_application_model_init():
    gr_application_model = GRApplicationModel()
    assert gr_application_model


def test_gr_application_model_attributes(mock_sqlalchemy_session):
    guardrail_id = 1
    application_id = 1
    application_name = "mock_application_name"
    application_key = "mock_application_key"

    gr_application_model = GRApplicationModel(
        guardrail_id=guardrail_id,
        application_id=application_id,
        application_name=application_name,
        application_key=application_key
    )

    assert gr_application_model.guardrail_id == guardrail_id
    assert gr_application_model.application_id == application_id
    assert gr_application_model.application_name == application_name
    assert gr_application_model.application_key == application_key

    # Test nullable constraints
    assert gr_application_model.guardrail_id is not None
    assert gr_application_model.application_id is not None
    assert gr_application_model.application_name is not None
    assert gr_application_model.application_key is not None


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


def test_guardrail_config_model_init():
    guardrail_config_model = GRConfigModel()
    assert guardrail_config_model


def test_guardrail_config_model_attributes():
    guardrail_id = 1
    guardrail_provider = GuardrailProvider.AWS
    response_message = "I couldn't respond to that message."
    config_type = "mock_config_type"
    config_data = {"mock_key": "mock_value"}

    guardrail_config_model = GRConfigModel(
        guardrail_id=guardrail_id,
        guardrail_provider=guardrail_provider,
        response_message=response_message,
        config_type=config_type,
        config_data=config_data
    )

    assert guardrail_config_model.guardrail_id == guardrail_id
    assert guardrail_config_model.guardrail_provider == guardrail_provider
    assert guardrail_config_model.response_message == response_message
    assert guardrail_config_model.config_type == config_type
    assert guardrail_config_model.config_data == config_data

    # Test nullable constraints
    assert guardrail_config_model.guardrail_id is not None
    assert guardrail_config_model.guardrail_provider is not None
    assert guardrail_config_model.response_message is not None
    assert guardrail_config_model.config_type is not None
    assert guardrail_config_model.config_data is not None


def test_gr_provider_response_model_init():
    gr_provider_response_model = GRProviderResponseModel()
    assert gr_provider_response_model


def test_gr_provider_response_model_attributes(mock_sqlalchemy_session):
    guardrail_id = 1
    guardrail_provider = GuardrailProvider.AWS
    response_data = {"mock_key": "mock_value"}

    gr_provider_response_model = GRProviderResponseModel(
        guardrail_id=guardrail_id,
        guardrail_provider=guardrail_provider,
        response_data=response_data
    )

    assert gr_provider_response_model.guardrail_id == guardrail_id
    assert gr_provider_response_model.guardrail_provider == guardrail_provider
    assert gr_provider_response_model.response_data == response_data

    # Test nullable constraints
    assert gr_provider_response_model.guardrail_id is not None
    assert gr_provider_response_model.guardrail_provider is not None
    assert gr_provider_response_model.response_data is not None


def test_gr_connection_mapping_model_init():
    gr_connection_mapping_model = GRConnectionMappingModel()
    assert gr_connection_mapping_model


def test_gr_connection_mapping_model_attributes(mock_sqlalchemy_session):
    guardrail_id = 1
    gr_connection_id = 1
    guardrail_provider = GuardrailProvider.AWS

    gr_connection_mapping_model = GRConnectionMappingModel(
        guardrail_id=guardrail_id,
        gr_connection_id=gr_connection_id,
        guardrail_provider=guardrail_provider
    )

    assert gr_connection_mapping_model.guardrail_id == guardrail_id
    assert gr_connection_mapping_model.gr_connection_id == gr_connection_id
    assert gr_connection_mapping_model.guardrail_provider == guardrail_provider

    # Test nullable constraints
    assert gr_connection_mapping_model.guardrail_id is not None
    assert gr_connection_mapping_model.gr_connection_id is not None
    assert gr_connection_mapping_model.guardrail_provider is not None


@pytest.fixture
def guardrail(mock_sqlalchemy_session):
    guardrail_instance = GuardrailModel(name="Mock Guardrail", description="A mock guardrail", version=1)
    mock_sqlalchemy_session.add(guardrail_instance)
    mock_sqlalchemy_session.commit()
    return guardrail_instance


@pytest.fixture
def guardrail_application(mock_sqlalchemy_session, guardrail):
    application_instance = GRApplicationModel(
        guardrail_id=guardrail.id,
        application_id=1001,
        application_name="Mock Application",
        application_key="mock_app_key"
    )
    mock_sqlalchemy_session.add(application_instance)
    mock_sqlalchemy_session.commit()
    return application_instance


@pytest.fixture
def guardrail_config(mock_sqlalchemy_session, guardrail):
    config_instance = GRConfigModel(
        guardrail_id=guardrail.id,
        guardrail_provider=GuardrailProvider.AWS,
        response_message="I couldn't respond to that message.",
        config_type=GuardrailConfigType.CONTENT_MODERATION,
        config_data={"mock_key": "mock_value"}
    )
    mock_sqlalchemy_session.add(config_instance)
    mock_sqlalchemy_session.commit()
    return config_instance


@pytest.fixture
def guardrail_provider_response(mock_sqlalchemy_session, guardrail):
    response_instance = GRProviderResponseModel(
        guardrail_id=guardrail.id,
        guardrail_provider=GuardrailProvider.AWS,
        response_data={"mock_key": "mock_value"}
    )
    mock_sqlalchemy_session.add(response_instance)
    mock_sqlalchemy_session.commit()
    return response_instance


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
def guardrail_connection_mapping(mock_sqlalchemy_session, guardrail, guardrail_connection):
    gr_connection_mapping_instance = GRConnectionMappingModel(
        guardrail_id=guardrail.id,
        gr_connection_id=guardrail_connection.id,
        guardrail_provider=GuardrailProvider.AWS
    )
    mock_sqlalchemy_session.add(gr_connection_mapping_instance)
    mock_sqlalchemy_session.commit()
    return gr_connection_mapping_instance


def test_guardrail_has_applications(mock_sqlalchemy_session, guardrail, guardrail_application):
    # Retrieve the guardrail from the database
    guardrail_from_db = mock_sqlalchemy_session.query(GuardrailModel).filter_by(name="Mock Guardrail").one()

    # Assert that the guardrail has the application associated with it
    assert len(guardrail_from_db.gr_application) == 1
    assert guardrail_from_db.gr_application[0].application_name == "Mock Application"
    assert guardrail_from_db.gr_application[0].application_key == "mock_app_key"


def test_application_has_guardrail(mock_sqlalchemy_session, guardrail_application):
    # Retrieve the application from the database
    application_from_db = mock_sqlalchemy_session.query(GRApplicationModel).filter_by(
        application_key="mock_app_key").one()

    # Assert that the application has the correct guardrail associated with it
    assert application_from_db.guardrail is not None
    assert application_from_db.guardrail.name == "Mock Guardrail"
    assert application_from_db.guardrail.description == "A mock guardrail"
    assert application_from_db.guardrail.version == 1


def test_guardrail_has_config(mock_sqlalchemy_session, guardrail, guardrail_config):
    # Retrieve the guardrail from the database
    guardrail_from_db = mock_sqlalchemy_session.query(GuardrailModel).filter_by(name="Mock Guardrail").one()

    # Assert that the guardrail has the configuration associated with it
    assert len(guardrail_from_db.gr_config) == 1
    assert guardrail_from_db.gr_config[0].guardrail_provider == GuardrailProvider.AWS
    assert guardrail_from_db.gr_config[0].config_type == GuardrailConfigType.CONTENT_MODERATION
    assert guardrail_from_db.gr_config[0].config_data == {"mock_key": "mock_value"}


def test_config_has_guardrail(mock_sqlalchemy_session, guardrail_config):
    # Retrieve the configuration from the database
    config_from_db = mock_sqlalchemy_session.query(GRConfigModel).filter_by(
        guardrail_provider=GuardrailProvider.AWS).one()

    # Assert that the configuration has the correct guardrail associated with it
    assert config_from_db.guardrail is not None
    assert config_from_db.guardrail.name == "Mock Guardrail"
    assert config_from_db.guardrail.description == "A mock guardrail"
    assert config_from_db.guardrail.version == 1
    assert config_from_db.guardrail.gr_config[0].response_message == "I couldn't respond to that message."
    assert config_from_db.guardrail.gr_config[0].config_type == GuardrailConfigType.CONTENT_MODERATION
    assert config_from_db.guardrail.gr_config[0].config_data == {"mock_key": "mock_value"}


def test_guardrail_has_provider_response(mock_sqlalchemy_session, guardrail, guardrail_provider_response):
    # Retrieve the guardrail from the database
    guardrail_from_db = mock_sqlalchemy_session.query(GuardrailModel).filter_by(name="Mock Guardrail").one()

    # Assert that the guardrail has the provider response associated with it
    assert len(guardrail_from_db.gr_response) == 1
    assert guardrail_from_db.gr_response[0].guardrail_provider == GuardrailProvider.AWS
    assert guardrail_from_db.gr_response[0].response_data == {"mock_key": "mock_value"}


def test_provider_response_has_guardrail(mock_sqlalchemy_session, guardrail_provider_response):
    # Retrieve the provider response from the database
    response_from_db = mock_sqlalchemy_session.query(GRProviderResponseModel).filter_by(
        guardrail_provider=GuardrailProvider.AWS).one()

    # Assert that the provider response has the correct guardrail associated with it
    assert response_from_db.guardrail is not None
    assert response_from_db.guardrail.name == "Mock Guardrail"
    assert response_from_db.guardrail.description == "A mock guardrail"
    assert response_from_db.guardrail.version == 1
    assert response_from_db.guardrail.gr_response[0].guardrail_provider == GuardrailProvider.AWS
    assert response_from_db.guardrail.gr_response[0].response_data == {"mock_key": "mock_value"}


def test_guardrail_has_connection_mapping(mock_sqlalchemy_session, guardrail, guardrail_connection_mapping):
    # Retrieve the guardrail from the database
    guardrail_from_db = mock_sqlalchemy_session.query(GuardrailModel).filter_by(name="Mock Guardrail").one()

    # Assert that the guardrail has the connection mapping associated with it
    assert len(guardrail_from_db.gr_connection_mapping) == 1
    assert guardrail_from_db.gr_connection_mapping[0].guardrail_provider == GuardrailProvider.AWS
    assert guardrail_from_db.gr_connection_mapping[0].gr_connection.name == "mock_connection"
    assert guardrail_from_db.gr_connection_mapping[0].gr_connection.description == "mock_description"
    assert guardrail_from_db.gr_connection_mapping[0].gr_connection.guardrail_provider == GuardrailProvider.AWS
    assert guardrail_from_db.gr_connection_mapping[0].gr_connection.connection_details == {"mock_key": "mock_value"}


def test_connection_mapping_has_guardrail(mock_sqlalchemy_session, guardrail_connection_mapping):
    # Retrieve the connection mapping from the database
    connection_mapping_from_db = mock_sqlalchemy_session.query(GRConnectionMappingModel).filter_by(
        guardrail_provider=GuardrailProvider.AWS).one()

    # Assert that the connection mapping has the correct guardrail associated with it
    assert connection_mapping_from_db.guardrail is not None
    assert connection_mapping_from_db.guardrail.name == "Mock Guardrail"
    assert connection_mapping_from_db.guardrail.description == "A mock guardrail"
    assert connection_mapping_from_db.guardrail.version == 1
    assert connection_mapping_from_db.gr_connection.name == "mock_connection"
    assert connection_mapping_from_db.gr_connection.description == "mock_description"
    assert connection_mapping_from_db.gr_connection.guardrail_provider == GuardrailProvider.AWS
    assert connection_mapping_from_db.gr_connection.connection_details == {"mock_key": "mock_value"}