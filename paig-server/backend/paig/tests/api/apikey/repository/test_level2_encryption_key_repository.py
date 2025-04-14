import pytest
from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService
from core.exceptions import NotFoundException
from api.apikey.controllers.paig_level2_encryption_key_controller import PaigLevel2EncryptionKeyController
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from api.apikey.database.db_operations.paig_level2_encryption_key_repository import PaigLevel2EncryptionKeyRepository
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from api.apikey.utils import EncryptionKeyStatus


@pytest.fixture()
def level2_repo(db_session, set_context_session) -> PaigLevel2EncryptionKeyRepository:
    return PaigLevel2EncryptionKeyRepository()

@pytest.fixture
def controller(db_session, set_context_session):
    level2_encryption_key_repository = PaigLevel2EncryptionKeyRepository()
    secure_encryptor_factory = SecureEncryptorFactory()

    paig_level2_key_service = PaigLevel2EncryptionKeyService(
        paig_level2_encryption_key_repository=level2_encryption_key_repository,
        secure_encryptor_factory=secure_encryptor_factory
    )

    controller_instance = PaigLevel2EncryptionKeyController()
    controller_instance._level2_encryption_key_service = paig_level2_key_service
    return controller_instance

@pytest.mark.asyncio
async def test_get_active_paig_level2_encryption_key(level2_repo, controller):
    from api.encryption.events.startup import create_encryption_master_key_if_not_exists
    await create_encryption_master_key_if_not_exists()

    # Create Level2 key
    created_key = await controller.create_paig_level2_encryption_key()
    result = await level2_repo.get_active_paig_level2_encryption_key()

    assert result.id == created_key.id
    assert result.key_status == EncryptionKeyStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_get_active_paig_level2_encryption_key_not_found(level2_repo):
    with pytest.raises(NotFoundException) as exc_info:
        await level2_repo.get_active_paig_level2_encryption_key()

    expected = get_error_message(
        ERROR_RESOURCE_NOT_FOUND, "Active Level2 Encryption key", "key_status", EncryptionKeyStatus.ACTIVE.value
    )
    assert expected in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_level2_encryption_key_by_id(level2_repo, controller):
    from api.encryption.events.startup import create_encryption_master_key_if_not_exists
    await create_encryption_master_key_if_not_exists()

    created_key = await controller.create_paig_level2_encryption_key()
    result = await level2_repo.get_paig_level2_encryption_key_by_id(created_key.id)

    assert result.id == created_key.id
    assert result.key_status == EncryptionKeyStatus.ACTIVE.value


@pytest.mark.asyncio
async def test_get_level2_encryption_key_by_id_not_found(level2_repo):
    with pytest.raises(NotFoundException) as exc_info:
        await level2_repo.get_paig_level2_encryption_key_by_id(999)

    expected = get_error_message(
        ERROR_RESOURCE_NOT_FOUND, "Level2 Encryption key", "keyId", 999
    )
    assert expected in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_paig_level2_encryption_key_by_uuid(level2_repo, controller):
    from api.encryption.events.startup import create_encryption_master_key_if_not_exists
    await create_encryption_master_key_if_not_exists()

    created_key = await controller.create_paig_level2_encryption_key()
    result = await level2_repo.get_paig_level2_encryption_key_by_uuid(created_key.key_id)

    assert result.key_id == created_key.key_id
    assert result.id == created_key.id


@pytest.mark.asyncio
async def test_get_paig_level2_encryption_key_by_uuid_not_found(level2_repo):
    fake_uuid = "non-existent-uuid"
    with pytest.raises(NotFoundException) as exc_info:
        await level2_repo.get_paig_level2_encryption_key_by_uuid(fake_uuid)

    expected = get_error_message(
        ERROR_RESOURCE_NOT_FOUND, "Level2 Encryption key", "keyUuid", fake_uuid
    )
    assert expected in str(exc_info.value)
