from unittest.mock import patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.guardrails import GuardrailProvider
from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails.database.db_operations.gr_connection_repository import GRConnectionRepository


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
