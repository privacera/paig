import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel, BaseSQLModel


# Mocking SQLAlchemy session for testing purposes
@pytest.fixture
def mock_sqlalchemy_session():
    engine = create_engine('sqlite:///:memory:')
    BaseSQLModel.metadata.create_all(engine)
    my_session = sessionmaker(bind=engine)
    session = my_session()
    yield session
    session.close()


def test_encryption_master_key_model_init():
    master_key_model = EncryptionMasterKeyModel()
    assert master_key_model


def test_encryption_master_key_model_attributes(mock_sqlalchemy_session):
    key_value = "mock_master_key"

    master_key_model = EncryptionMasterKeyModel(
        key=key_value
    )

    assert master_key_model.key == key_value

    # Test nullable constraint
    assert master_key_model.key is not None
