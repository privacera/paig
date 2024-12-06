from unittest.mock import patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.guardrails import GuardrailProvider
from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails.database.db_models.guardrail_model import GRConnectionMappingModel
from api.guardrails.database.db_models.guardrail_view_model import GRConnectionViewModel
from api.guardrails.database.db_operations.gr_connection_repository import GRConnectionRepository, \
    GRConnectionMappingRepository, GRConnectionViewRepository


@pytest.fixture
def mock_guardrail_connection_repository():
    return GRConnectionRepository()


@pytest.mark.asyncio
async def test_get_guardrail_connection(mock_guardrail_connection_repository):
    mock_guardrail_connection = GRConnectionModel(
        id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"mock_key": "mock_value"}
    )

    with patch.object(GRConnectionRepository, 'get_all', return_value=[mock_guardrail_connection]):
        result = await mock_guardrail_connection_repository.get_all()
        assert len(result) == 1
        assert result[0].name == "mock_name"
        assert result[0].description == "mock_description"
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].connection_details == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_connection_by_id(mock_guardrail_connection_repository):
    key_id = 1
    mock_guardrail_connection = GRConnectionModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"mock_key": "mock_value"}
    )

    with patch.object(GRConnectionRepository, 'get_record_by_id', return_value=mock_guardrail_connection):
        result = await mock_guardrail_connection_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.connection_details == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_get_guardrail_connection_by_id_not_found(mock_guardrail_connection_repository):
    key_id = 0

    with patch.object(GRConnectionRepository, 'get_by', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_guardrail_connection_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_guardrail_connection(mock_guardrail_connection_repository):
    mock_guardrail_connection = GRConnectionModel(
        id=1,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"mock_key": "mock_value"}
    )

    with patch.object(GRConnectionRepository, 'create', return_value=mock_guardrail_connection):
        result = await mock_guardrail_connection_repository.create(mock_guardrail_connection)
        assert result.id == 1
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.connection_details == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_update_guardrail_connection(mock_guardrail_connection_repository):
    key_id = 1
    mock_guardrail_connection = GRConnectionModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"mock_key": "mock_value"}
    )

    with patch.object(GRConnectionRepository, 'update', return_value=mock_guardrail_connection):
        result = await mock_guardrail_connection_repository.update(mock_guardrail_connection)
        assert result.id == key_id
        assert result.name == "mock_name"
        assert result.description == "mock_description"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.connection_details == {"mock_key": "mock_value"}


@pytest.mark.asyncio
async def test_delete_guardrail_connection(mock_guardrail_connection_repository):
    key_id = 1
    mock_guardrail_connection = GRConnectionModel(
        id=key_id,
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"mock_key": "mock_value"}
    )

    with patch.object(GRConnectionRepository, 'delete', return_value=None):
        result = await mock_guardrail_connection_repository.delete(mock_guardrail_connection)
        assert result is None


@pytest.fixture
def mock_gr_connection_mapping_repository():
    return GRConnectionMappingRepository()


@pytest.fixture
def mock_gr_connection_view_repository():
    return GRConnectionViewRepository()

@pytest.mark.asyncio
async def test_get_guardrail_connection_mapping_by_guardrail_id(mock_gr_connection_mapping_repository):
    mock_gr_connection_mapping = GRConnectionMappingModel(
        guardrail_id=1,
        gr_connection_id=1,
        guardrail_provider=GuardrailProvider.AWS
    )

    with patch.object(GRConnectionMappingRepository, 'get_all', return_value=[mock_gr_connection_mapping]):
        result = await mock_gr_connection_mapping_repository.get_all(filters={"guardrail_id": 1})
        assert len(result) == 1
        assert result[0].guardrail_id == 1
        assert result[0].gr_connection_id == 1
        assert result[0].guardrail_provider == GuardrailProvider.AWS


@pytest.mark.asyncio
async def test_create_guardrail_connection_mapping(mock_gr_connection_mapping_repository):
    mock_gr_connection_mapping = GRConnectionMappingModel(
        guardrail_id=1,
        gr_connection_id=1,
        guardrail_provider=GuardrailProvider.AWS
    )

    with patch.object(GRConnectionMappingRepository, 'create', return_value=mock_gr_connection_mapping):
        result = await mock_gr_connection_mapping_repository.create(mock_gr_connection_mapping)
        assert result.guardrail_id == 1
        assert result.gr_connection_id == 1
        assert result.guardrail_provider == GuardrailProvider.AWS


@pytest.mark.asyncio
async def test_delete_guardrail_connection_mapping(mock_gr_connection_mapping_repository):
    mock_gr_connection_mapping = GRConnectionMappingModel(
        guardrail_id=1,
        gr_connection_id=1,
        guardrail_provider=GuardrailProvider.AWS
    )

    with patch.object(GRConnectionMappingRepository, 'delete', return_value=None):
        result = await mock_gr_connection_mapping_repository.delete(mock_gr_connection_mapping)
        assert result is None


@pytest.mark.asyncio
async def test_get_guardrail_connection_view_by_guardrail_id(mock_gr_connection_view_repository):
    mock_gr_connection_view = GRConnectionViewModel(
        name="mock_name",
        description="mock_description",
        guardrail_provider=GuardrailProvider.AWS,
        connection_details={"mock_key": "mock_value"},
        guardrail_id=1
    )

    with patch.object(GRConnectionViewRepository, 'get_all', return_value=[mock_gr_connection_view]):
        result = await mock_gr_connection_view_repository.get_all(filters={"guardrail_id": 1})
        assert len(result) == 1
        assert result[0].name == "mock_name"
        assert result[0].description == "mock_description"
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].connection_details == {"mock_key": "mock_value"}
        assert result[0].guardrail_id == 1
