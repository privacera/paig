from api.governance.services.ai_app_service import AIAppRequestValidator, AIAppService
from api.governance.database.db_operations.ai_app_repository import AIAppRepository
from api.governance.database.db_operations.vector_db_repository import VectorDBRepository
from api.apikey.services.paig_level1_encryption_key_service import PaigLevel1EncryptionKeyService
from api.apikey.services.paig_level2_encryption_key_service import PaigLevel2EncryptionKeyService
from api.encryption.factory.secure_encryptor_factory import SecureEncryptorFactory
from api.apikey.database.db_operations.paig_api_key_repository import PaigApiKeyRepository
from api.apikey.services.paig_api_key_service import PaigApiKeyService
from api.apikey.database.db_operations.paig_level1_encryption_key_repository import PaigLevel1EncryptionKeyRepository
from api.apikey.database.db_operations.paig_level2_encryption_key_repository import PaigLevel2EncryptionKeyRepository
from api.encryption.events.startup import create_default_encryption_keys
import pytest
from datetime import timezone



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


@pytest.fixture
def token_expiry_date():
    from datetime import datetime, timedelta
    return datetime.now() + timedelta(days=30)

@pytest.fixture
def api_key_data(token_expiry_date):
    return {
        "api_key_name": "Test app api key",
        "application_id": 111,
        "description": "Test description",
        "expiry": token_expiry_date,
    }


@pytest.mark.asyncio
async def test_create_api_key(service, token_expiry_date, api_key_data):
    await create_default_encryption_keys()

    user_id = 123
    created_key = await service.create_api_key(api_key_data, user_id)

    assert created_key is not None
    assert created_key["userId"] == user_id
    assert created_key["apiKeyName"] == api_key_data["api_key_name"]
    assert created_key["applicationId"] == api_key_data["application_id"]
    assert created_key["description"] == api_key_data["description"]
    assert created_key["tokenExpiry"] == api_key_data["expiry"].replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds')


@pytest.mark.asyncio
async def test_get_api_key_by_ids(service, token_expiry_date, api_key_data):
    await create_default_encryption_keys()

    user_id = 123

    created_key = await service.create_api_key(api_key_data, user_id)
    key_id = created_key["id"]

    result = await service.get_api_key_by_ids([key_id])

    assert len(result) == 1
    assert result[0]["id"] == key_id


@pytest.mark.asyncio
async def test_get_api_keys_by_application_id(service, api_key_data):
    await create_default_encryption_keys()

    user_id = 123

    created_key = await service.create_api_key(api_key_data, user_id)
    key_id = created_key["id"]
    page = 0
    size = 10
    sort = ['tokenExpiry,DESC']
    key_status = ['ACTIVE', 'DISABLED', 'EXPIRED']
    include_filters = {'exact_match': False}

    api_key_results, total_count = await service.get_api_keys_by_application_id(
        api_key_data["application_id"], include_filters, page, size, sort, key_status
    )

    assert len(api_key_results) == 1
    assert api_key_results[0].id == key_id
    assert total_count == 1

    # Test with partial match
    include_filters = {
        'api_key_name': 'Test',
        'exact_match': False
    }
    api_key_results, total_count = await service.get_api_keys_by_application_id(
        api_key_data["application_id"], include_filters, page, size, sort, key_status
    )
    assert len(api_key_results) == 1
    assert api_key_results[0].id == key_id
    assert total_count == 1

    # Test with exact match
    include_filters = {
        'api_key_name': 'Test app api key',
        'exact_match': True
    }
    api_key_results, total_count = await service.get_api_keys_by_application_id(
        api_key_data["application_id"], include_filters, page, size, sort, key_status
    )

    assert len(api_key_results) == 1
    assert api_key_results[0].id == key_id
    assert total_count == 1

    # Test with no results
    include_filters = {
        'api_key_name': 'Non-existing key',
        'exact_match': True
    }

    api_key_results, total_count = await service.get_api_keys_by_application_id(
        api_key_data["application_id"], include_filters, page, size, sort, key_status
    )

    assert len(api_key_results) == 0
    assert total_count == 0

    # Test with no results and exact match false
    include_filters = {
        'api_key_name': 'Non-existing',
        'exact_match': False
    }

    api_key_results, total_count = await service.get_api_keys_by_application_id(
        api_key_data["application_id"], include_filters, page, size, sort, key_status
    )

    assert len(api_key_results) == 0
    assert total_count == 0


@pytest.mark.asyncio
async def test_disable_api_key(service, token_expiry_date, api_key_data):
    await create_default_encryption_keys()

    user_id = 123

    created_key = await service.create_api_key(api_key_data, user_id)
    key_id = created_key["id"]

    result = await service.disable_api_key(key_id)

    assert result is not None
    assert result["keyStatus"] == "DISABLED"
    assert result["id"] == key_id


@pytest.mark.asyncio
async def test_permanent_delete_api_key(service, token_expiry_date, api_key_data):
    await create_default_encryption_keys()

    user_id = 123

    created_key = await service.create_api_key(api_key_data, user_id)
    key_id = created_key["id"]

    result = await service.permanent_delete_api_key(key_id)

    assert result is not None
    assert result== "API Key deleted successfully"


    # Check if the key is actually deleted
    deleted_key = await service.get_api_key_by_ids([key_id])
    assert len(deleted_key) == 0




