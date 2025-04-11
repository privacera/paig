import pytest
from api.apikey.utils import APIKeyStatus
from api.apikey.database.db_operations.paig_api_key_repository import PaigApiKeyRepository
from core.exceptions import NotFoundException

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

@pytest.mark.asyncio
async def test_create_and_get_by_id(key_params, repo):
    created_key = await repo.create_api_key(key_params)

    assert created_key.id is not None
    assert created_key.user_id == key_params["user_id"]
    assert created_key.api_key_name == key_params["api_key_name"]
    assert created_key.key_id == key_params["key_id"]
    assert created_key.application_id == key_params["application_id"]
    assert created_key.key_status == key_params["key_status"]
    assert created_key.api_key_masked == key_params["api_key_masked"]

@pytest.mark.asyncio
async def test_get_api_key_by_ids_success(key_params, repo):
    created_key = await repo.create_api_key(key_params)
    keys = await repo.get_api_key_by_ids([created_key.id])
    assert len(keys) == 1
    assert keys[0].key_id == key_params["key_id"]


@pytest.mark.asyncio
async def test_get_api_key_by_ids_invalid_id(repo):
    keys = await repo.get_api_key_by_ids([999])
    assert len(keys) == 0


@pytest.mark.asyncio
async def test_get_paig_api_key_by_uuid_success(key_params, repo):
    await repo.create_api_key(key_params)
    key = await repo.get_paig_api_key_by_uuid(key_params["key_id"])
    assert key is not None
    assert key.key_id == key_params["key_id"]


@pytest.mark.asyncio
async def test_get_paig_api_key_by_uuid_not_found(repo):
    with pytest.raises(NotFoundException) as e:
        await repo.get_paig_api_key_by_uuid("nonexistent-uuid")
    assert "keyUuid" in str(e.value)


@pytest.mark.asyncio
async def test_disable_api_key_success(key_params, repo):
    created_key = await repo.create_api_key(key_params)
    disabled_key = await repo.disable_api_key(created_key.id)
    assert disabled_key.key_status == APIKeyStatus.DISABLED.value


@pytest.mark.asyncio
async def test_disable_api_key_not_found(repo):
    with pytest.raises(NotFoundException) as e:
        await repo.disable_api_key(9999)
    assert "keyId" in str(e.value)


@pytest.mark.asyncio
async def test_permanent_delete_api_key_success(key_params, repo):
    created_key = await repo.create_api_key(key_params)
    message = await repo.permanent_delete_api_key(created_key.id)
    assert message == "API Key deleted successfully"


@pytest.mark.asyncio
async def test_permanent_delete_api_key_not_found(repo):
    with pytest.raises(NotFoundException) as e:
        await repo.permanent_delete_api_key(12345)
    assert "keyId" in str(e.value)


@pytest.mark.asyncio
async def test_get_api_keys_by_application_id(key_params, repo):
    await repo.create_api_key(key_params)
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
