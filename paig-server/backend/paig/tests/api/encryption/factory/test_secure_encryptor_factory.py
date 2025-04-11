import pytest
from unittest.mock import AsyncMock

from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel
from api.encryption.database.db_operations.encryption_master_key_repository import EncryptionMasterKeyRepository
from api.encryption.utils.secure_encryptor import SecureEncryptor
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from api.encryption.events.startup import create_encryption_master_key_if_not_exists


@pytest.fixture
def encryption_master_key_repository():
    return EncryptionMasterKeyRepository()


@pytest.mark.asyncio
async def test_get_secure_encryptor(encryption_master_key_repository, db_session, set_context_session):
    await create_encryption_master_key_if_not_exists()

    secure_encryptor_factory = SecureEncryptorFactory(encryption_master_key_repository)

    # Call the method to be tested
    secure_encryptor = await secure_encryptor_factory.get_or_create_secure_encryptor()

    # Assertions
    assert isinstance(secure_encryptor, SecureEncryptor)
