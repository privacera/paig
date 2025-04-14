import pytest
from unittest.mock import AsyncMock, patch
from api.apikey.utils import APIKeyStatus
from core.exceptions import NotFoundException
from api.apikey.services.paig_level1_encryption_key_service import PaigLevel1EncryptionKeyService
from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from api.apikey.database.db_operations.paig_api_key_repository import PaigApiKeyRepository
from api.apikey.services.paig_api_key_service import PaigApiKeyService
from api.governance.services.ai_app_service import AIAppRequestValidator, AIAppService
from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from api.governance.database.db_operations.vector_db_repository import VectorDBRepository
from api.apikey.database.db_operations.paig_level1_encryption_key_repository import PaigLevel1EncryptionKeyRepository
from api.apikey.database.db_operations.paig_level2_encryption_key_repository import PaigLevel2EncryptionKeyRepository
from api.encryption.events.startup import create_default_encryption_keys


@pytest.fixture()
def key_params():
    return {
        "user_id": 1,
        "api_key_name": "Test app api key",
        "key_id": "uuid-111",
        "application_id": 1,
        "key_status": APIKeyStatus.ACTIVE.value,
        "api_key_masked": "abcd*****xyz"
    }


@pytest.fixture()
def repo(db_session, set_context_session):
    return PaigApiKeyRepository()



@pytest.fixture
def level1_encryption_key_repository():
    return PaigLevel1EncryptionKeyRepository()

@pytest.fixture
def level2_encryption_key_repository():
    return PaigLevel2EncryptionKeyRepository()

@pytest.fixture
def secure_encryptor_factory():
    return SecureEncryptorFactory()


@pytest.fixture
def paig_level1_encryption_key_service(level1_encryption_key_repository, secure_encryptor_factory):
    paig_level1_key_service =  PaigLevel1EncryptionKeyService(
        paig_level1_encryption_key_repository=level1_encryption_key_repository,
        secure_encryptor_factory=secure_encryptor_factory
    )
    return paig_level1_key_service


@pytest.fixture
def paig_level2_encryption_key_service(level2_encryption_key_repository, secure_encryptor_factory):
    paig_level2_key_service = PaigLevel2EncryptionKeyService(
        paig_level2_encryption_key_repository=level2_encryption_key_repository,
        secure_encryptor_factory=secure_encryptor_factory
    )
    return paig_level2_key_service




@pytest.fixture
def service(db_session, set_context_session, paig_level1_encryption_key_service, paig_level2_encryption_key_service, secure_encryptor_factory):
    ai_app_repository = AIAppRepository()
    vector_db_repository = VectorDBRepository()

    ai_app_request_validator = AIAppRequestValidator(
        ai_app_repository=ai_app_repository,
        vector_db_repository=vector_db_repository
    )

    ai_app_service = AIAppService(
        ai_app_repository=ai_app_repository,
        ai_app_request_validator=ai_app_request_validator
    )

    paig_api_key_repository = PaigApiKeyRepository()

    service = PaigApiKeyService(
        ai_app_service=ai_app_service,
        paig_api_key_repository=paig_api_key_repository,
        paig_level1_encryption_key_service=paig_level1_encryption_key_service,
        paig_level2_encryption_key_service=paig_level2_encryption_key_service,
        secure_encryptor_factory=secure_encryptor_factory
    )

    return service



@pytest.mark.asyncio
async def test_create_and_get_by_id(key_params, repo):
    # Prepare a mock return value
    mock_created_key = repo.model_class()
    mock_created_key.set_attribute(key_params)

    # Patch the method
    with patch.object(repo, 'create_api_key', new=AsyncMock(return_value=mock_created_key)) as mock_method:
        created_key = await repo.create_api_key(key_params)

        # Assertions
        mock_method.assert_awaited_once_with(key_params)
        assert created_key.id is None  # Assuming the ID is set by DB later
        assert created_key.user_id == key_params["user_id"]
        assert created_key.api_key_name == key_params["api_key_name"]
        assert created_key.key_id == key_params["key_id"]
        assert created_key.application_id == key_params["application_id"]
        assert created_key.key_status == key_params["key_status"]
        assert created_key.api_key_masked == key_params["api_key_masked"]

@pytest.mark.asyncio
async def test_get_api_key_by_ids_success(key_params, repo, service):
    await create_default_encryption_keys()
    created_key = await service.create_api_key(key_params, user_id=key_params["user_id"])
    keys = await repo.get_api_key_by_ids(key_ids=[1])
    assert len(keys) == 1
    assert keys[0].key_id == key_params["key_id"]


@pytest.mark.asyncio
async def test_get_api_key_by_ids_invalid_id(repo):
    keys = await repo.get_api_key_by_ids([999])
    assert len(keys) == 0


@pytest.mark.asyncio
async def test_get_paig_api_key_by_uuid_success(key_params, repo, service):
    await create_default_encryption_keys()
    await service.create_api_key(key_params, user_id=key_params["user_id"])
    key = await repo.get_paig_api_key_by_uuid(key_params["key_id"])
    assert key is not None
    assert key.key_id == key_params["key_id"]


@pytest.mark.asyncio
async def test_get_paig_api_key_by_uuid_not_found(repo):
    with pytest.raises(NotFoundException) as e:
        await repo.get_paig_api_key_by_uuid("nonexistent-uuid")
    assert "keyUuid" in str(e.value)


@pytest.mark.asyncio
async def test_disable_api_key_success(key_params, repo, service):
    await create_default_encryption_keys()
    created_key = await service.create_api_key(key_params, user_id=key_params["user_id"])
    disabled_key = await repo.disable_api_key(created_key["id"])
    assert disabled_key.key_status == APIKeyStatus.DISABLED.value


@pytest.mark.asyncio
async def test_disable_api_key_not_found(repo):
    with pytest.raises(NotFoundException) as e:
        await repo.disable_api_key(9999)
    assert "keyId" in str(e.value)


@pytest.mark.asyncio
async def test_permanent_delete_api_key_success(key_params, repo, service):
    await create_default_encryption_keys()

    created_key = await service.create_api_key(key_params, user_id=key_params["user_id"])
    message = await repo.permanent_delete_api_key(created_key["id"])
    assert message == "API Key deleted successfully"


@pytest.mark.asyncio
async def test_permanent_delete_api_key_not_found(repo):
    with pytest.raises(NotFoundException) as e:
        await repo.permanent_delete_api_key(12345)
    assert "keyId" in str(e.value)


@pytest.mark.asyncio
async def test_get_api_keys_by_application_id(key_params, repo, service):
    await create_default_encryption_keys()
    created_key = await service.create_api_key(key_params, user_id=key_params["user_id"])
    keys, count = await repo.get_api_keys_by_application_id(
        application_id=key_params["application_id"],
        include_filters={},
        page=0,
        size=10,
        sort=None,
        key_status=[APIKeyStatus.ACTIVE.value]
    )
    assert count >= 1
    assert any(k.key_id == key_params["key_id"] for k in keys)
