import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService
from api.apikey.services.paig_encryption_views import PaigLevel2EncryptionKeyView
from core.exceptions import NotFoundException
from api.apikey.utils import EncryptionKeyStatus


@pytest.fixture
def mock_repository():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_encryptor():
    encryptor = AsyncMock()
    encryptor.encrypt.return_value = "encrypted-key"
    return encryptor


@pytest.fixture
def mock_encryptor_factory(mock_encryptor):
    factory = AsyncMock()
    factory.get_or_create_secure_encryptor.return_value = mock_encryptor
    return factory


@pytest.fixture
def service(mock_repository, mock_encryptor_factory):
    return PaigLevel2EncryptionKeyService(
        paig_level2_encryption_key_repository=mock_repository,
        secure_encryptor_factory=mock_encryptor_factory
    )


@pytest.mark.asyncio
async def test_create_key_no_active_key(service, mock_repository, mock_encryptor_factory):
    mock_repository.get_active_paig_level2_encryption_key.side_effect = NotFoundException("No active key")

    mock_created = PaigLevel2EncryptionKeyView(
        key_id="uuid123",
        paig_key_value="encrypted-key",
        key_status=EncryptionKeyStatus.ACTIVE.value
    )
    service.create_record = AsyncMock(return_value=mock_created)

    result = await service.create_paig_level2_encryption_key()

    assert result.key_id == "uuid123"
    assert result.paig_key_value == "encrypted-key"
    assert result.key_status == EncryptionKeyStatus.ACTIVE.value
    service.create_record.assert_called_once()


@pytest.mark.asyncio
async def test_create_key_with_existing_active_key(service, mock_repository):
    existing_key = MagicMock()
    existing_key.id = "existing-id"
    mock_repository.get_active_paig_level2_encryption_key.return_value = existing_key

    with patch("api.apikey.services.paig_encryption_views.PaigLevel2EncryptionKeyView.model_validate") as mock_validate:
        updated_view = PaigLevel2EncryptionKeyView(key_status=EncryptionKeyStatus.PASSIVE.value)
        mock_validate.return_value = updated_view

        service.update_record = AsyncMock()
        service.create_record = AsyncMock(return_value=PaigLevel2EncryptionKeyView(
            key_id="uuid123", paig_key_value="encrypted-key", key_status=EncryptionKeyStatus.ACTIVE.value
        ))

        result = await service.create_paig_level2_encryption_key()

        service.update_record.assert_called_once_with("existing-id", updated_view)
        assert result.key_status == EncryptionKeyStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_get_key_by_id(service, mock_repository):
    mock_repository.get_paig_level2_encryption_key_by_id.return_value = "some-key"
    result = await service.get_paig_level2_encryption_key_by_id("key123")
    assert result == "some-key"
    mock_repository.get_paig_level2_encryption_key_by_id.assert_called_once_with("key123")


@pytest.mark.asyncio
async def test_get_key_by_uuid(service, mock_repository):
    mock_repository.get_paig_level2_encryption_key_by_uuid.return_value = "uuid-key"
    result = await service.get_paig_level2_encryption_key_by_uuid("uuid123")
    assert result == "uuid-key"
    mock_repository.get_paig_level2_encryption_key_by_uuid.assert_called_once_with("uuid123")


@pytest.mark.asyncio
async def test_get_key_by_uuid_not_found(service, mock_repository):
    mock_repository.get_paig_level2_encryption_key_by_uuid.side_effect = NotFoundException("not found")
    result = await service.get_paig_level2_encryption_key_by_uuid("invalid")
    assert result is None


@pytest.mark.asyncio
async def test_delete_key(service, mock_repository):
    mock_repository.delete_by.return_value = True
    result = await service.delete_paig_level2_encryption_key("del-id")
    assert result is True
    mock_repository.delete_by.assert_called_once_with(filters={"id": "del-id"})


@pytest.mark.asyncio
async def test_get_active_key_not_found(service, mock_repository):
    mock_repository.get_active_paig_level2_encryption_key.side_effect = NotFoundException("no active key")
    result = await service.get_active_paig_level2_encryption_key()
    assert result is None
