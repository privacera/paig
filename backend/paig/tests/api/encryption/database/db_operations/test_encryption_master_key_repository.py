from datetime import datetime

import pytest
from unittest.mock import patch
from core.exceptions import NotFoundException
from api.encryption.database.db_models.encryption_master_key_model import EncryptionMasterKeyModel
from api.encryption.database.db_operations.encryption_master_key_repository import EncryptionMasterKeyRepository


@pytest.fixture
def mock_encryption_master_key_repository():
    return EncryptionMasterKeyRepository()


@pytest.mark.asyncio
async def test_get_active_encryption_master_key(mock_encryption_master_key_repository):
    mock_encryption_master_key = EncryptionMasterKeyModel(
        id=1, key="some_master_key", create_time=datetime.now(), update_time=datetime.now()
    )

    with patch.object(EncryptionMasterKeyRepository, 'get_all',
                      return_value=[mock_encryption_master_key]):
        result = await mock_encryption_master_key_repository.get_active_encryption_master_key()
        assert result == mock_encryption_master_key


@pytest.mark.asyncio
async def test_get_active_encryption_master_key_not_found(mock_encryption_master_key_repository):
    with patch.object(EncryptionMasterKeyRepository, 'get_all', return_value=[]):
        with pytest.raises(NotFoundException) as exc_info:
            await mock_encryption_master_key_repository.get_active_encryption_master_key()

        assert str(exc_info.value) == "Encryption master key not found"
