import pytest
from unittest.mock import AsyncMock

from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel
from api.encryption.database.db_operations.encryption_master_key_repository import EncryptionMasterKeyRepository
from api.encryption.utils.secure_encryptor import SecureEncryptor
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory


@pytest.fixture
def mock_encryption_master_key_repository():
    return AsyncMock(spec=EncryptionMasterKeyRepository)


@pytest.mark.asyncio
async def test_get_secure_encryptor(mock_encryption_master_key_repository):
    # Create a mock encryption master key model
    mock_master_key = EncryptionMasterKeyModel(id=1, key="test_master_key")

    # Configure the mock repository to return the mock master key
    mock_encryption_master_key_repository.get_active_encryption_master_key.return_value = mock_master_key

    secure_encryptor_factory = SecureEncryptorFactory(mock_encryption_master_key_repository)

    # Call the method to be tested
    secure_encryptor = await secure_encryptor_factory.get_or_create_secure_encryptor()

    # Assertions
    assert isinstance(secure_encryptor, SecureEncryptor)
    mock_encryption_master_key_repository.get_active_encryption_master_key.assert_called_once()
