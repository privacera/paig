import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.db_models.BaseSQLModel import BaseSQLModel
from api.guardrails.database.db_models.response_template_model import ResponseTemplateModel

# Set up a SQLite in-memory database for testing
@pytest.fixture(scope="module")
def setup_test_database():
    engine = create_engine("sqlite:///:memory:")
    BaseSQLModel.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield TestingSessionLocal
    BaseSQLModel.metadata.drop_all(engine)

@pytest.fixture
def db_session(setup_test_database):
    session = setup_test_database()
    yield session
    session.close()

def test_response_template_creation(db_session):
    """
    Test creating a ResponseTemplateModel instance and saving it to the database.
    """
    new_template = ResponseTemplateModel(
        response="This is a test response",
        description="Test description"
    )
    db_session.add(new_template)
    db_session.commit()

    # Query the database to verify
    fetched_template = db_session.query(ResponseTemplateModel).filter_by(response="This is a test response").first()
    assert fetched_template is not None
    assert fetched_template.response == "This is a test response"
    assert fetched_template.description == "Test description"

def test_response_template_with_null_description(db_session):
    """
    Test creating a ResponseTemplateModel instance with a null description.
    """
    new_template = ResponseTemplateModel(response="Response without description")
    db_session.add(new_template)
    db_session.commit()

    # Query the database to verify
    fetched_template = db_session.query(ResponseTemplateModel).filter_by(response="Response without description").first()
    assert fetched_template is not None
    assert fetched_template.response == "Response without description"
    assert fetched_template.description is None

def test_response_template_update(db_session):
    """
    Test updating an existing ResponseTemplateModel instance.
    """
    new_template = ResponseTemplateModel(
        response="Old response",
        description="Old description"
    )
    db_session.add(new_template)
    db_session.commit()

    # Update the template
    new_template.response = "Updated response"
    new_template.description = "Updated description"
    db_session.commit()

    # Query the database to verify
    updated_template = db_session.query(ResponseTemplateModel).filter_by(response="Updated response").first()
    assert updated_template is not None
    assert updated_template.response == "Updated response"
    assert updated_template.description == "Updated description"

def test_response_template_deletion(db_session):
    """
    Test deleting a ResponseTemplateModel instance.
    """
    new_template = ResponseTemplateModel(
        response="To be deleted",
        description="Delete me"
    )
    db_session.add(new_template)
    db_session.commit()

    # Delete the template
    db_session.delete(new_template)
    db_session.commit()

    # Query the database to verify deletion
    deleted_template = db_session.query(ResponseTemplateModel).filter_by(response="To be deleted").first()
    assert deleted_template is None
