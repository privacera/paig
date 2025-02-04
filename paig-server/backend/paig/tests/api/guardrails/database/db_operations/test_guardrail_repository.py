from unittest.mock import patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.guardrails import GuardrailProvider
from api.guardrails.database.db_models.guardrail_model import GuardrailModel, \
    GRApplicationVersionModel, GRVersionHistoryModel
from api.guardrails.database.db_operations.guardrail_repository import GuardrailRepository, GRVersionHistoryRepository, \
    GRApplicationVersionRepository


@pytest.fixture
def mock_guardrail_repository():
    return GuardrailRepository()


@pytest.mark.asyncio
async def test_get_guardrail(mock_guardrail_repository):
    mock_guardrail = GuardrailModel(
        id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1
    )

    with patch.object(GuardrailRepository, 'get_all', return_value=[mock_guardrail]):
        result = await mock_guardrail_repository.get_all()
        assert len(result) == 1
        assert result[0].name == "mock_name"
        assert result[0].description == "mock_description"
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].guardrail_connection_name == "mock_connection_name"
        assert result[0].version == 1


@pytest.mark.asyncio
async def test_get_guardrail_by_id(mock_guardrail_repository):
    key_id = 1
    mock_guardrail = GuardrailModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1
    )

    with patch.object(GuardrailRepository, 'get_record_by_id', return_value=mock_guardrail):
        result = await mock_guardrail_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_connection_name == "mock_connection_name"
        assert result.version == 1


@pytest.mark.asyncio
async def test_get_guardrail_by_id_not_found(mock_guardrail_repository):
    key_id = 0

    with patch.object(GuardrailRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail(mock_guardrail_repository):
    mock_guardrail = GuardrailModel(
        id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1
    )

    with patch.object(GuardrailRepository, 'create', return_value=mock_guardrail):
        result = await mock_guardrail_repository.create(mock_guardrail)
        assert result.id == 1
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_connection_name == "mock_connection_name"
        assert result.version == 1


@pytest.mark.asyncio
async def test_update_guardrail(mock_guardrail_repository):
    key_id = 1
    mock_guardrail = GuardrailModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1
    )

    with patch.object(GuardrailRepository, 'update', return_value=mock_guardrail):
        result = await mock_guardrail_repository.update(mock_guardrail)
        assert result.id == key_id
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_connection_name == "mock_connection_name"
        assert result.version == 1


@pytest.mark.asyncio
async def test_delete_guardrail(mock_guardrail_repository):
    key_id = 1
    mock_guardrail = GuardrailModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1
    )

    with patch.object(GuardrailRepository, 'delete', return_value=None):
        result = await mock_guardrail_repository.delete(mock_guardrail)
        assert result is None


@pytest.fixture
def mock_guardrail_version_history_repository():
    return GRVersionHistoryRepository()


@pytest.mark.asyncio
async def test_get_guardrail_version_history(mock_guardrail_version_history_repository):
    mock_guardrail_version_history = GRVersionHistoryModel(
        id=1,
        guardrail_id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1,
        application_keys=["mock_app_key"],
        guardrail_configs=[{
            "config_type": "mock_config_type",
            "config_data": {"mock_key": "mock_value"},
            "response_message": "mock_response_message"
        }],
        guardrail_provider_response={"AWS": {"success": True, "response": {"mock_key": "mock_value"}}}
    )

    with patch.object(GRVersionHistoryRepository, 'get_all', return_value=[mock_guardrail_version_history]):
        result = await mock_guardrail_version_history_repository.get_all()
        assert len(result) == 1
        assert result[0].guardrail_id == 1
        assert result[0].application_keys == ["mock_app_key"]
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].guardrail_connection_name == "mock_connection_name"
        assert result[0].version == 1
        assert result[0].guardrail_configs == [{
            "config_type": "mock_config_type",
            "config_data": {"mock_key": "mock_value"},
            "response_message": "mock_response_message"
        }]
        assert result[0].guardrail_provider_response == {
            "AWS": {"success": True, "response": {"mock_key": "mock_value"}}
        }


@pytest.mark.asyncio
async def test_create_guardrail_version_history(mock_guardrail_version_history_repository):
    mock_guardrail_version_history = GRVersionHistoryModel(
        id=1,
        guardrail_id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1,
        application_keys=["mock_app_key"],
        guardrail_configs=[{
            "config_type": "mock_config_type",
            "config_data": {"mock_key": "mock_value"},
            "response_message": "mock_response_message"
        }],
        guardrail_provider_response={"AWS": {"success": True, "response": {"mock_key": "mock_value"}}}
    )

    with patch.object(GRVersionHistoryRepository, 'create', return_value=mock_guardrail_version_history):
        result = await mock_guardrail_version_history_repository.create(mock_guardrail_version_history)
        assert result.id == 1
        assert result.guardrail_id == 1
        assert result.application_keys == ["mock_app_key"]
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_connection_name == "mock_connection_name"
        assert result.version == 1


@pytest.mark.asyncio
async def test_update_guardrail_version_history(mock_guardrail_version_history_repository):
    key_id = 1
    mock_guardrail_version_history = GRVersionHistoryModel(
        id=key_id,
        guardrail_id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1,
        application_keys=["mock_app_key"],
        guardrail_configs=[{
            "config_type": "mock_config_type",
            "config_data": {"mock_key": "mock_value"},
            "response_message": "mock_response_message"
        }],
        guardrail_provider_response={"AWS": {"success": True, "response": {"mock_key": "mock_value"}}}
    )

    with patch.object(GRVersionHistoryRepository, 'update', return_value=mock_guardrail_version_history):
        result = await mock_guardrail_version_history_repository.update(mock_guardrail_version_history)
        assert result.id == key_id
        assert result.guardrail_id == 1
        assert result.application_keys == ["mock_app_key"]
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.guardrail_connection_name == "mock_connection_name"
        assert result.version == 1


@pytest.mark.asyncio
async def test_delete_guardrail_version_history(mock_guardrail_version_history_repository):
    key_id = 1
    mock_guardrail_version_history = GRVersionHistoryModel(
        id=key_id,
        guardrail_id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        guardrail_connection_name="mock_connection_name",
        version=1
    )

    with patch.object(GRVersionHistoryRepository, 'delete', return_value=None):
        result = await mock_guardrail_version_history_repository.delete(mock_guardrail_version_history)
        assert result is None


@pytest.fixture
def mock_guardrail_application_version_repository():
    return GRApplicationVersionRepository()


@pytest.mark.asyncio
async def test_get_guardrail_application_version(mock_guardrail_application_version_repository):
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=1,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'get_all', return_value=[mock_guardrail_application_version]):
        result = await mock_guardrail_application_version_repository.get_all()
        assert len(result) == 1
        assert result[0].application_key == "mock_app_key"
        assert result[0].version == 1


@pytest.mark.asyncio
async def test_get_guardrail_application_version_by_id(mock_guardrail_application_version_repository):
    key_id = 1
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=key_id,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'get_record_by_id',
                      return_value=mock_guardrail_application_version):
        result = await mock_guardrail_application_version_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.application_key == "mock_app_key"
        assert result.version == 1


@pytest.mark.asyncio
async def test_get_guardrail_application_version_by_id_not_found(mock_guardrail_application_version_repository):
    key_id = 0

    with patch.object(GRApplicationVersionRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_application_version_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail_application_version(mock_guardrail_application_version_repository):
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=1,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'create', return_value=mock_guardrail_application_version):
        result = await mock_guardrail_application_version_repository.create(mock_guardrail_application_version)
        assert result.id == 1
        assert result.application_key == "mock_app_key"
        assert result.version == 1


@pytest.mark.asyncio
async def test_update_guardrail_application_version(mock_guardrail_application_version_repository):
    key_id = 1
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=key_id,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'update', return_value=mock_guardrail_application_version):
        result = await mock_guardrail_application_version_repository.update(mock_guardrail_application_version)
        assert result.id == key_id
        assert result.application_key == "mock_app_key"
        assert result.version == 1


@pytest.mark.asyncio
async def test_delete_guardrail_application_version(mock_guardrail_application_version_repository):
    key_id = 1
    mock_guardrail_application_version = GRApplicationVersionModel(
        id=key_id,
        application_key="mock_app_key",
        version=1
    )

    with patch.object(GRApplicationVersionRepository, 'delete', return_value=None):
        result = await mock_guardrail_application_version_repository.delete(mock_guardrail_application_version)
        assert result is None
