import pytest
from api.apikey.services.paig_level1_encryption_key_service import PaigLevel1EncryptionKeyService
from api.apikey.controllers.paig_level1_encryption_key_controller import PaigLevel1EncryptionKeyController
from api.apikey.database.db_operations.paig_level1_encryption_key_repository import PaigLevel1EncryptionKeyRepository
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from api.apikey.utils import EncryptionKeyStatus


@pytest.fixture
def controller(db_session, set_context_session):
    level1_encryption_key_repository = PaigLevel1EncryptionKeyRepository()
    secure_encryptor_factory = SecureEncryptorFactory()

    paig_level1_key_service =  PaigLevel1EncryptionKeyService(
        paig_level1_encryption_key_repository=level1_encryption_key_repository,
        secure_encryptor_factory=secure_encryptor_factory
    )
    controller_instance = PaigLevel1EncryptionKeyController()
    controller_instance._level1_encryption_key_service = paig_level1_key_service

    return controller_instance


@pytest.fixture()
def repo(db_session, set_context_session) -> PaigLevel1EncryptionKeyRepository:
    return PaigLevel1EncryptionKeyRepository()


@pytest.mark.asyncio
async def test_get_active_paig_level1_encryption_key(repo, controller):
    from api.encryption.events.startup import create_encryption_master_key_if_not_exists
    await create_encryption_master_key_if_not_exists()

    created_key = await controller.create_paig_level1_encryption_key()
    result = await repo.get_active_paig_level1_encryption_key()

    assert result.id == created_key.id
    assert result.key_status == EncryptionKeyStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_get_active_paig_level1_encryption_key_not_found(repo):
    # No active key in db
    with pytest.raises(NotFoundException) as exc_info:
        await repo.get_active_paig_level1_encryption_key()

    expected = get_error_message(
        ERROR_RESOURCE_NOT_FOUND, "Active Level1 Encryption key", "key_status", EncryptionKeyStatus.ACTIVE.value
    )
    assert expected in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_level1_encryption_key_by_id(repo, controller):
    from api.encryption.events.startup import create_encryption_master_key_if_not_exists
    await create_encryption_master_key_if_not_exists()


    created_key = await controller.create_paig_level1_encryption_key()

    result = await repo.get_paig_level1_encryption_key_by_id(created_key.id)

    assert result.id == created_key.id
    assert result.key_status == EncryptionKeyStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_get_level1_encryption_key_by_id_not_found(repo):
    with pytest.raises(NotFoundException) as exc_info:
        await repo.get_paig_level1_encryption_key_by_id(999)

    expected = get_error_message(
        ERROR_RESOURCE_NOT_FOUND, "Level1 Encryption key", "keyId", 999
    )
    assert expected in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_paig_level1_encryption_key_by_uuid(repo, controller):
    from api.encryption.events.startup import create_encryption_master_key_if_not_exists
    await create_encryption_master_key_if_not_exists()

    created_key = await controller.create_paig_level1_encryption_key()

    result = await repo.get_paig_level1_encryption_key_by_uuid(created_key.key_id)

    assert result.key_id == created_key.key_id
    assert result.id == created_key.id


@pytest.mark.asyncio
async def test_get_paig_level1_encryption_key_by_uuid_not_found(repo):
    fake_uuid = "non-existent-uuid"
    with pytest.raises(NotFoundException) as exc_info:
        await repo.get_paig_level1_encryption_key_by_uuid(fake_uuid)

    expected = get_error_message(
        ERROR_RESOURCE_NOT_FOUND, "Level1 Encryption key", "keyUuid", fake_uuid
    )
    assert expected in str(exc_info.value)
