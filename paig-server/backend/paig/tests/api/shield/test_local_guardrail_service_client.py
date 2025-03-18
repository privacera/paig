import pytest
from unittest.mock import AsyncMock, patch
from core.controllers.paginated_response import Pageable
from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter
from api.shield.client.local_guardrail_service_client import LocalGuardrailServiceClient


@pytest.fixture
def mock_guardrail_service():
    """Mock the GuardrailService dependency."""
    from api.guardrails.services.guardrails_service import GuardrailService
    mock_service = AsyncMock(spec=GuardrailService)
    return mock_service


@pytest.fixture
def service_client(mock_guardrail_service):
    """Patch SingletonDepends to return the mock service and initialize the client."""
    with patch("api.shield.client.local_guardrail_service_client.SingletonDepends", return_value=mock_guardrail_service):
        return LocalGuardrailServiceClient()


@pytest.mark.asyncio
async def test_get_guardrail_info_by_id_valid(service_client, mock_guardrail_service):
    """Test get_guardrail_info_by_id with a valid guardrail ID."""
    mock_guardrail = AsyncMock(spec=GuardrailView)
    mock_guardrail.model_dump.return_value = {"id": 1, "name": "Test Guardrail"}
    mock_guardrail_service.get_by_id.return_value = mock_guardrail

    result = await service_client.get_guardrail_info_by_id("tenant123", 1)

    assert result == {"id": 1, "name": "Test Guardrail"}
    mock_guardrail_service.get_by_id.assert_called_once_with(1, extended=True)


@pytest.mark.asyncio
async def test_get_guardrail_info_by_id_invalid(service_client, mock_guardrail_service):
    """Test get_guardrail_info_by_id with an invalid guardrail ID."""
    mock_guardrail_service.get_by_id.return_value = None

    result = await service_client.get_guardrail_info_by_id("tenant123", 999)

    assert result == {}
    mock_guardrail_service.get_by_id.assert_called_once_with(999, extended=True)


@pytest.mark.asyncio
async def test_get_guardrail_info_by_name_valid(service_client, mock_guardrail_service):
    """Test get_guardrail_info_by_name with a valid guardrail name."""
    mock_guardrail = AsyncMock(spec=GuardrailView)
    mock_guardrail.model_dump.return_value = {"id": 1, "name": "Test Guardrail"}

    pageable_result = Pageable(content=[mock_guardrail], totalElements=1, totalPages=1, size=1, number=0, numberOfElements=1, last=True, first=True, sort=[], empty=False)
    mock_guardrail_service.list.return_value = pageable_result

    result = await service_client.get_guardrail_info_by_name("tenant123", ["Test Guardrail"])

    assert result == {"id": 1, "name": "Test Guardrail"}
    mock_guardrail_service.list.assert_called_once_with(filter=GuardrailFilter(name="Test Guardrail", extended=True))


@pytest.mark.asyncio
async def test_get_guardrail_info_by_name_invalid(service_client, mock_guardrail_service):
    """Test get_guardrail_info_by_name with an invalid guardrail name."""
    pageable_result = Pageable(content=[], totalElements=0, totalPages=1, size=1, number=0, numberOfElements=0, last=True, first=True, sort=[], empty=True)
    mock_guardrail_service.list.return_value = pageable_result

    result = await service_client.get_guardrail_info_by_name("tenant123", ["Invalid Guardrail"])

    assert result == {}
    mock_guardrail_service.list.assert_called_once_with(filter=GuardrailFilter(name="Invalid Guardrail", extended=True))

@pytest.mark.asyncio
async def test_get_guardrail_info_by_name_multiple_names(service_client, mock_guardrail_service):
    """Test get_guardrail_info_by_name when multiple names are passed."""
    mock_guardrail = AsyncMock(spec=GuardrailView)
    mock_guardrail.model_dump.return_value = {"id": 1, "name": "First Guardrail"}

    pageable_result = Pageable(content=[mock_guardrail], totalElements=1, totalPages=1, size=1, number=0, numberOfElements=1, last=True, first=True, sort=[], empty=False)
    mock_guardrail_service.list.return_value = pageable_result

    result = await service_client.get_guardrail_info_by_name("tenant123", ["First Guardrail", "Second Guardrail"])

    assert result == {"id": 1, "name": "First Guardrail"}
    mock_guardrail_service.list.assert_called_once_with(filter=GuardrailFilter(name="First Guardrail", extended=True))