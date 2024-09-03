import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from paig_common.encryption import RSAKeyInfo

from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from core.exceptions import NotFoundException
from api.encryption.api_schemas.encryption_key import EncryptionKeyView, EncryptionKeyFilter
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyModel, EncryptionKeyType, \
    EncryptionKeyStatus
from api.encryption.database.db_operations.encryption_key_repository import EncryptionKeyRepository
from api.encryption.utils.secure_encryptor import SecureEncryptor
from api.encryption.services.encryption_key_service import EncryptionKeyService, EncryptionKeyRequestValidator


@pytest.fixture
def mock_encryption_key_repository():
    return AsyncMock(spec=EncryptionKeyRepository)


@pytest.fixture
def mock_secure_encryptor_factory():
    return AsyncMock(spec=SecureEncryptorFactory)


@pytest.fixture
def mock_secure_encryptor():
    return AsyncMock(spec=SecureEncryptor)


@pytest.fixture
def mock_encryption_key_request_validator():
    return AsyncMock(spec=EncryptionKeyRequestValidator)


@pytest.fixture
def encryption_key_service(mock_encryption_key_repository, mock_secure_encryptor_factory, mock_secure_encryptor,
                           mock_encryption_key_request_validator):
    mock_secure_encryptor.encrypt.side_effect = lambda x: f"encrypted_{x}"
    mock_secure_encryptor_factory.get_or_create_secure_encryptor.return_value = mock_secure_encryptor
    return EncryptionKeyService(
        encryption_key_repository=mock_encryption_key_repository,
        secure_encryptor_factory=mock_secure_encryptor_factory,
        encryption_key_request_validator=mock_encryption_key_request_validator
    )


@pytest.mark.asyncio
async def test_list_encryption_keys(encryption_key_service, mock_encryption_key_repository, mock_secure_encryptor):
    mock_filter = EncryptionKeyFilter()
    mock_sort = ["create_time"]
    mock_pageable = MagicMock()
    mock_pageable.content = [EncryptionKeyView(public_key="encrypted_pub_key", private_key="encrypted_priv_key")]

    with patch.object(encryption_key_service, 'list_records', return_value=mock_pageable):
        result = await encryption_key_service.list_encryption_keys(mock_filter, page_number=1, size=10, sort=mock_sort)
        assert len(result.content) == 1
        assert mock_secure_encryptor.decrypt.called


@pytest.mark.asyncio
async def test_create_encryption_key(encryption_key_service, mock_encryption_key_repository, mock_secure_encryptor,
                                     mock_encryption_key_request_validator):
    key_type = EncryptionKeyType.MSG_PROTECT_SHIELD
    rsa_key_info = RSAKeyInfo(public_key_encoded_str="pub_key", private_key_encoded_str="priv_key")

    mock_encryption_key_repository.get_active_encryption_key_by_type.side_effect = NotFoundException
    with patch('paig_common.encryption.RSAKeyUtil.generate_key_pair', return_value=rsa_key_info):
        result = await encryption_key_service.create_encryption_key(key_type)
        assert result.key_type == key_type
        assert mock_secure_encryptor.encrypt.call_count == 2
        assert mock_encryption_key_repository.create_record.called


@pytest.mark.asyncio
async def test_get_public_encryption_key_by_id(encryption_key_service, mock_encryption_key_repository,
                                               mock_secure_encryptor):
    mock_encryption_key_view = EncryptionKeyView(id=1, public_key="encrypted_pub_key")

    mock_encryption_key_repository.get_record_by_id.return_value = mock_encryption_key_view
    result = await encryption_key_service.get_public_encryption_key_by_id(1)
    assert result.id == 1
    assert mock_secure_encryptor.decrypt.called


@pytest.mark.asyncio
async def test_get_encryption_key_by_id(encryption_key_service, mock_encryption_key_repository, mock_secure_encryptor):
    mock_encryption_key_view = EncryptionKeyView(id=1, public_key="encrypted_pub_key", private_key="encrypted_priv_key")

    mock_encryption_key_repository.get_record_by_id.return_value = mock_encryption_key_view
    result = await encryption_key_service.get_encryption_key_by_id(1)
    assert result.id == 1
    assert mock_secure_encryptor.decrypt.call_count == 2


@pytest.mark.asyncio
async def test_get_active_encryption_key_by_type(encryption_key_service, mock_encryption_key_repository,
                                                 mock_secure_encryptor, mock_encryption_key_request_validator):
    key_type = EncryptionKeyType.MSG_PROTECT_SHIELD
    mock_encryption_key_model = EncryptionKeyModel(public_key="encrypted_pub_key", private_key="encrypted_priv_key")

    mock_encryption_key_repository.get_active_encryption_key_by_type.return_value = mock_encryption_key_model
    mock_secure_encryptor.decrypt.return_value = "decrypted_pub_key"
    result = await encryption_key_service.get_active_encryption_key_by_type(key_type)
    assert result.public_key == "decrypted_pub_key"
    assert mock_secure_encryptor.decrypt.call_count == 2
    assert mock_encryption_key_request_validator.validate_key_type.called


@pytest.mark.asyncio
async def test_delete_disabled_encryption_key(encryption_key_service, mock_encryption_key_repository,
                                              mock_encryption_key_request_validator):
    mock_encryption_key_view = EncryptionKeyView(id=1, key_status=EncryptionKeyStatus.DISABLED)
    with patch("core.controllers.base_controller.BaseController.update_record",
               AsyncMock(return_value=mock_encryption_key_view)):
        mock_encryption_key_repository.get_encryption_key_by_id.return_value = mock_encryption_key_view
        await encryption_key_service.delete_disabled_encryption_key(1)
        assert mock_encryption_key_request_validator.validate_delete_request.called


@pytest.mark.asyncio
async def test_disable_passive_encryption_key(encryption_key_service, mock_encryption_key_repository,
                                              mock_encryption_key_request_validator):
    mock_encryption_key_view = EncryptionKeyView(id=1, key_status=EncryptionKeyStatus.PASSIVE)
    with patch("core.controllers.base_controller.BaseController.update_record", AsyncMock(return_value=mock_encryption_key_view)):

        mock_encryption_key_repository.get_encryption_key_by_id.return_value = mock_encryption_key_view
        await encryption_key_service.disable_passive_encryption_key(1)
        assert mock_encryption_key_request_validator.validate_disable_request.called
