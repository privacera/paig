from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.exc import NoResultFound

from api.guardrails import GuardrailProvider
from api.guardrails.api_schemas.gr_connection import GRConnectionFilter, GRConnectionView
from api.guardrails.database.db_models.gr_connection_model import GRConnectionModel
from api.guardrails.database.db_operations.gr_connection_repository import GRConnectionRepository
from api.guardrails.services.gr_connections_service import GRConnectionRequestValidator, GRConnectionService
from core.exceptions import BadRequestException, NotFoundException

gr_connection_view_json = {
    "id": 1,
    "status": 1,
    "createTime": "2024-10-29T13:03:27.000000",
    "updateTime": "2024-10-29T13:03:27.000000",
    "name": "gr_connection_1",
    "description": "test description1",
    "guardrailsProvider": "AWS",
    "connectionDetails": {
        "access_key": "mock_access_key",
        "secret_key": "mock_secret_key",
        "session_token": "mock_session_token"
    }
}

gr_connection_view = GRConnectionView(**gr_connection_view_json)


@pytest.fixture
def mock_guardrail_connection_repository():
    return AsyncMock(spec=GRConnectionRepository)


@pytest.fixture
def guardrail_connection_request_validator(mock_guardrail_connection_repository):
    return GRConnectionRequestValidator(gr_connection_repository=mock_guardrail_connection_repository)


@pytest.fixture
def guardrail_connection_service(mock_guardrail_connection_repository, guardrail_connection_request_validator):
    return GRConnectionService(
        gr_connection_repository=mock_guardrail_connection_repository,
        gr_connection_request_validator=guardrail_connection_request_validator
    )


@pytest.mark.asyncio
async def test_list_guardrail_connections(guardrail_connection_service, mock_guardrail_connection_repository):
    mock_filter = GRConnectionFilter()
    mock_sort = ["create_time"]
    expected_records = [gr_connection_view]
    expected_total_count = 100
    # Patch the list_records method on the repository
    with patch.object(
        mock_guardrail_connection_repository, 'list_records', return_value=(expected_records, expected_total_count)
    ) as mock_list_records:

        # Call the method under test
        result = await guardrail_connection_service.list(filter=mock_filter, page_number=1, size=10, sort=mock_sort)

        # Assertions
        mock_list_records.assert_called_once_with(filter=mock_filter, page_number=1, size=10, sort=mock_sort)
        assert result.content == expected_records
        assert result.totalElements == expected_total_count


@pytest.mark.asyncio
async def test_list_guardrail_connection_provider_names(guardrail_connection_service, mock_guardrail_connection_repository):
    expected_records = [gr_connection_view]
    # Patch the list_records method on the repository
    with patch.object(
        mock_guardrail_connection_repository, 'list_records', return_value=(expected_records, 2)
    ) as mock_list_records:

        # Call the method under test
        result = await guardrail_connection_service.list_connection_provider_names()

        # Assertions
        mock_list_records.assert_called_once_with(
            cardinality="guardrail_provider",
            filter=GRConnectionFilter(),
        )
        assert result == [GuardrailProvider.AWS]



@pytest.mark.asyncio
async def test_create_guardrail_connection(guardrail_connection_service, mock_guardrail_connection_repository):
    with patch.object(
        mock_guardrail_connection_repository, 'create_record', return_value=gr_connection_view
    ) as mock_create_record, patch.object(
        mock_guardrail_connection_repository, 'list_records', return_value=(None, 0)
    ) as mock_get_by_name:
        # Call the method under test
        result = await guardrail_connection_service.create(gr_connection_view)

        # Assertions
        assert result == gr_connection_view
        assert mock_create_record.called
        assert mock_get_by_name.called


@pytest.mark.asyncio
async def test_create_guardrail_connection_when_name_already_exists(guardrail_connection_service, mock_guardrail_connection_repository):
    with patch.object(
        mock_guardrail_connection_repository, 'list_records', return_value=([gr_connection_view], 1)
    ) as mock_get_by_name:
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_connection_service.create(gr_connection_view)

        # Assertions
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail Connection already exists with name: ['gr_connection_1']"
        assert mock_get_by_name.called
        assert not mock_guardrail_connection_repository.create_record.called


@pytest.mark.asyncio
async def test_get_guardrail_connection_by_id(guardrail_connection_service, mock_guardrail_connection_repository):
    with patch.object(
            mock_guardrail_connection_repository, 'get_record_by_id', return_value=gr_connection_view
    ) as mock_get_record_by_id:
        # Call the method under test
        result = await guardrail_connection_service.get_by_id(1)

        # Assertions
        mock_get_record_by_id.assert_called_with(1)
        assert result == gr_connection_view


@pytest.mark.asyncio
async def test_get_guardrail_connection_by_id_when_not_found(guardrail_connection_service, mock_guardrail_connection_repository):
    with patch.object(
            mock_guardrail_connection_repository, 'get_record_by_id', side_effect=NoResultFound
    ) as mock_get_record_by_id:
        # Call the method under test
        with pytest.raises(NotFoundException) as exc_info:
            await guardrail_connection_service.get_by_id(1)

        # Assertions
        mock_get_record_by_id.assert_called_once_with(1)
        assert exc_info.type == NotFoundException
        assert exc_info.value.message == "Guardrail Connection not found with ID: [1]"


@pytest.mark.asyncio
async def test_update_guardrail_connection(guardrail_connection_service, mock_guardrail_connection_repository):
    with (patch.object(
        mock_guardrail_connection_repository, 'update_record', return_value=gr_connection_view
    ) as mock_update_record, patch.object(
        mock_guardrail_connection_repository, 'get_record_by_id', return_value=GRConnectionModel(id=1)
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_connection_repository, 'list_records', return_value=([gr_connection_view], 1)
    ) as mock_get_by_name):
        # Call the method under test
        result = await guardrail_connection_service.update(1, gr_connection_view)

        # Assertions
        assert result == gr_connection_view
        assert mock_update_record.called
        assert mock_get_record_by_id.called
        assert mock_get_by_name.called


@pytest.mark.asyncio
async def test_update_guardrail_connection_when_name_already_exists(guardrail_connection_service, mock_guardrail_connection_repository):
    with patch.object(
        mock_guardrail_connection_repository, 'get_record_by_id', return_value=GRConnectionModel(id=2)
    ) as mock_get_record_by_id, patch.object(
        mock_guardrail_connection_repository, 'list_records', return_value=([gr_connection_view], 1)
    ) as mock_get_by_name:
        # Call the method under test
        with pytest.raises(BadRequestException) as exc_info:
            await guardrail_connection_service.update(2, gr_connection_view)

        # Assertions
        assert exc_info.type == BadRequestException
        assert exc_info.value.message == "Guardrail Connection already exists with name: ['gr_connection_1']"
        assert not mock_guardrail_connection_repository.update_record.called
        assert mock_get_record_by_id.called
        assert mock_get_by_name.called


@pytest.mark.asyncio
async def test_delete_guardrail_connection(guardrail_connection_service, mock_guardrail_connection_repository):
    with patch.object(
        mock_guardrail_connection_repository, 'delete_record', return_value=None
    ) as mock_delete_record, patch.object(
        mock_guardrail_connection_repository, 'get_record_by_id', return_value=GRConnectionModel()
    ) as mock_get_record_by_id:
        # Call the method under test
        await guardrail_connection_service.delete(1)

        # Assertions
        assert mock_delete_record.called
        assert mock_get_record_by_id.called
