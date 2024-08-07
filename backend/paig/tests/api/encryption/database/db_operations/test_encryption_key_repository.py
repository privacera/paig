import pytest
from unittest.mock import patch
from sqlalchemy.exc import NoResultFound
from core.exceptions import NotFoundException
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType, EncryptionKeyModel, \
    EncryptionKeyStatus
from api.encryption.database.db_operations.encryption_key_repository import EncryptionKeyRepository


@pytest.fixture
def mock_encryption_key_repository():
    return EncryptionKeyRepository()


@pytest.mark.asyncio
async def test_get_active_encryption_key_by_type(mock_encryption_key_repository):
    key_type = EncryptionKeyType.MSG_PROTECT_SHIELD
    mock_encryption_key = EncryptionKeyModel(
        id=1, key_type=key_type, key_status=EncryptionKeyStatus.ACTIVE,
        public_key="public_key", private_key="private_key"
    )

    with patch.object(EncryptionKeyRepository, 'get_by', return_value=mock_encryption_key):
        result = await mock_encryption_key_repository.get_active_encryption_key_by_type(key_type)
        assert result.key_type == key_type
        assert result.key_status == EncryptionKeyStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_encryption_key_by_id(mock_encryption_key_repository):
    key_id = 2
    key_status = EncryptionKeyStatus.PASSIVE
    mock_encryption_key = EncryptionKeyModel(
        id=key_id, key_type=EncryptionKeyType.MSG_PROTECT_PLUGIN, key_status=key_status,
        public_key="public_key", private_key="private_key"
    )

    with patch.object(EncryptionKeyRepository, 'get_by', return_value=mock_encryption_key):
        result = await mock_encryption_key_repository.get_encryption_key_by_id(key_id, key_status)
        assert result.id == key_id
        assert result.key_status == key_status


@pytest.mark.asyncio
async def test_get_active_encryption_key_by_type_not_found(mock_encryption_key_repository):
    key_type = EncryptionKeyType.MSG_PROTECT_PLUGIN

    with patch.object(EncryptionKeyRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NotFoundException) as exc_info:
            await mock_encryption_key_repository.get_active_encryption_key_by_type(key_type)

        assert str(exc_info.value) == f"Active encryption key not found with key_type: {key_type.value}"


@pytest.mark.asyncio
async def test_get_encryption_key_by_id_not_found(mock_encryption_key_repository):
    key_id = 999
    key_status = EncryptionKeyStatus.PASSIVE

    with patch.object(EncryptionKeyRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NotFoundException) as exc_info:
            await mock_encryption_key_repository.get_encryption_key_by_id(key_id, key_status)

        assert str(exc_info.value) == f"{key_status.value} encryption key not found with ID: {key_id}"
