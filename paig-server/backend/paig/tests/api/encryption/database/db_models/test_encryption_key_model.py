import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.encryption.database.db_models.encryption_key_model import (EncryptionKeyModel, EncryptionKeyStatus,
                                                                EncryptionKeyType, BaseSQLModel)


# Mocking SQLAlchemy session for testing purposes
@pytest.fixture
def mock_sqlalchemy_session():
    engine = create_engine('sqlite:///:memory:')
    BaseSQLModel.metadata.create_all(engine)
    my_session = sessionmaker(bind=engine)
    session = my_session()
    yield session
    session.close()


def test_encryption_key_model_init():
    key_model = EncryptionKeyModel()
    assert key_model


def test_encryption_key_model_attributes(mock_sqlalchemy_session):
    public_key = "mock_public_key"
    private_key = "mock_private_key"
    key_status = EncryptionKeyStatus.ACTIVE
    key_type = EncryptionKeyType.MSG_PROTECT_SHIELD

    key_model = EncryptionKeyModel(
        public_key=public_key,
        private_key=private_key,
        key_status=key_status,
        key_type=key_type
    )

    assert key_model.public_key == public_key
    assert key_model.private_key == private_key
    assert key_model.key_status == key_status
    assert key_model.key_type == key_type

    # Test nullable constraints
    assert key_model.public_key is not None
    assert key_model.private_key is not None
    assert key_model.key_status is not None
    assert key_model.key_type is not None
