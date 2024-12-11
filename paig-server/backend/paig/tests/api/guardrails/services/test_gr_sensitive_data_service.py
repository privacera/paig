from unittest.mock import AsyncMock, patch
import pytest

from api.guardrails import GuardrailProvider
from api.guardrails.database.db_operations.gr_sensitive_data_repository import GRSensitiveDataRepository
from core.exceptions import BadRequestException
from api.guardrails.services.gr_sensitive_data_service import GRSensitiveDataRequestValidator, GRSensitiveDataService
from api.guardrails.database.db_models.gr_sensitive_data_model import GRSensitiveDataModel
from api.guardrails.api_schemas.gr_sensitive_data import GRSensitiveDataView, GRSensitiveDataFilter


@pytest.fixture
def mock_gr_sensitive_data_repository():
    return AsyncMock(spec=GRSensitiveDataRepository)


@pytest.fixture
def request_validator(mock_gr_sensitive_data_repository):
    return GRSensitiveDataRequestValidator(gr_sensitive_data_repository=mock_gr_sensitive_data_repository)


@pytest.fixture
def service(mock_gr_sensitive_data_repository, request_validator):
    """Fixture for initializing the GRSensitiveDataService."""
    return GRSensitiveDataService(
        gr_sensitive_data_repository=mock_gr_sensitive_data_repository,
        gr_sensitive_data_request_validator=request_validator
    )


@pytest.mark.asyncio
async def test_validate_create_request_when_valid(request_validator, mock_gr_sensitive_data_repository):
    valid_request = GRSensitiveDataView(name="sensitive_data_1", label="label_1", guardrail_provider=GuardrailProvider.AWS)

    # Mock repository behavior for existing data
    mock_gr_sensitive_data_repository.list_records.return_value = ([], 0)

    # Validate create request
    await request_validator.validate_create_request(valid_request)

    mock_gr_sensitive_data_repository.list_records.assert_called()


@pytest.mark.asyncio
async def test_validate_create_request_when_name_exists(request_validator, mock_gr_sensitive_data_repository):
    existing_data = GRSensitiveDataModel(name="sensitive_data_1", label="label_1", guardrail_provider=GuardrailProvider.AWS)
    mock_gr_sensitive_data_repository.list_records.return_value = ([existing_data], 1)
    invalid_request = GRSensitiveDataView(name="sensitive_data_1", label="label_2", guardrail_provider=GuardrailProvider.AWS)

    with pytest.raises(BadRequestException) as exc_info:
        await request_validator.validate_create_request(invalid_request)

    # Assertions
    assert "already exists" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_create_request_when_label_exists(request_validator, mock_gr_sensitive_data_repository):
    existing_data = GRSensitiveDataModel(name="sensitive_data_2", label="label_2", guardrail_provider=GuardrailProvider.AWS)
    mock_gr_sensitive_data_repository.list_records.return_value = ([existing_data], 1)
    invalid_request = GRSensitiveDataView(name="sensitive_data_3", label="label_2", guardrail_provider=GuardrailProvider.AWS)

    with pytest.raises(BadRequestException) as exc_info:
        await request_validator.validate_create_request(invalid_request)

    # Assertions
    assert "already exists" in str(exc_info.value)


def test_validate_read_request(request_validator):
    # Valid ID
    valid_id = 1
    request_validator.validate_read_request(valid_id)
    # No exception means success


@pytest.mark.asyncio
async def test_validate_read_request_when_invalid(request_validator):
    invalid_id = -1  # Invalid ID
    with pytest.raises(BadRequestException) as exc_info:
        await request_validator.validate_read_request(invalid_id)

    # Assertions
    assert "Guardrail Sensitive Data ID" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_gr_sensitive_data_exists_raises_bad_request_exception(request_validator):
    # Mock the request_validator method to return a matching entry for name or label
    request_validator.get_gr_sensitive_data = AsyncMock()

    gr_sensitive_data_view_json = {
        "id": 1,
        "name": "Sensitive Data 1",
        "label": "Sensitive Label 1",
        "status": 1,
        "createTime": "2024-10-29T13:03:27.000000",
        "updateTime": "2024-10-29T13:03:27.000000",
        "response": "Test response",
        "description": "Test description",
        "guardrail_provider": "AWS"  # Assuming guardrail_provider is an enum or string
    }

    gr_sensitive_data_view = GRSensitiveDataView(**gr_sensitive_data_view_json)

    # Simulating a match by name
    request_validator.get_gr_sensitive_data.return_value = gr_sensitive_data_view

    # Prepare the request with duplicate name or label
    duplicate_request = GRSensitiveDataView(
        id=2,  # Different ID to trigger the conflict
        name="Sensitive Data 1",  # Same name as the one in gr_sensitive_data_view
        label="New Label",  # A new label that doesn't conflict
        status=1,
        response="Test response",
        description="Test description",
        guardrail_provider="AWS"
    )

    # Ensure BadRequestException is raised when trying to create a duplicate entry
    with pytest.raises(BadRequestException) as exc_info:
        await request_validator.validate_gr_sensitive_data_exists(duplicate_request)

    # Check if the error message contains relevant information
    assert "Guardrail Sensitive Data" in str(exc_info.value)
    assert "name" in str(exc_info.value)
    assert "Sensitive Data 1" in str(exc_info.value)
    assert "with provider ['AWS']" in str(exc_info.value)


@pytest.mark.asyncio
async def test_validate_update_request_when_valid(request_validator, mock_gr_sensitive_data_repository):
    valid_request = GRSensitiveDataView(name="updated_name", label="updated_label", guardrail_provider=GuardrailProvider.AWS)
    mock_gr_sensitive_data_repository.list_records.return_value = ([], 0)

    # Validate update request
    await request_validator.validate_update_request(1, valid_request)


def test_validate_delete_request(request_validator):
    # Valid ID
    valid_id = 1
    request_validator.validate_delete_request(valid_id)
    # No exception means success


@pytest.mark.asyncio
async def test_validate_create_request(request_validator, mock_gr_sensitive_data_repository):
    """Test the create request validation for GRSensitiveData."""
    mock_request = GRSensitiveDataView(name="Test Data", label="Test Label", guardrail_provider="AWS")
    mock_gr_sensitive_data_repository.list_records.return_value = ([], 0)

    await request_validator.validate_create_request(mock_request)
    mock_gr_sensitive_data_repository.list_records.assert_called()

@pytest.mark.asyncio
async def test_validate_create_request_existing_data(request_validator, mock_gr_sensitive_data_repository):
    """Test create request validation when GRSensitiveData already exists."""
    mock_request = GRSensitiveDataView(name="Test Data", label="Test Label", guardrail_provider="AWS")
    existing_data = GRSensitiveDataModel(id=1, name="Test Data", label="Test Label", guardrail_provider="AWS")
    mock_gr_sensitive_data_repository.list_records.return_value = ([existing_data], 1)

    with pytest.raises(BadRequestException):
        await request_validator.validate_create_request(mock_request)

@pytest.mark.asyncio
async def test_create_gr_sensitive_data(service, request_validator, mock_gr_sensitive_data_repository):
    """Test creating a new GRSensitiveData."""
    mock_request = GRSensitiveDataView(name="New Data", label="New Label", guardrail_provider="AWS")

    mock_gr_sensitive_data_repository.list_records.return_value = ([], 0)
    mock_gr_sensitive_data_repository.create_record.return_value = GRSensitiveDataModel(id=1, name="New Data", label="New Label", guardrail_provider="AWS")

    result = await service.create_gr_sensitive_data(mock_request)
    assert result.name == "New Data"
    assert result.label == "New Label"
    assert result.guardrail_provider == "AWS"

@pytest.mark.asyncio
async def test_update_gr_sensitive_data(service, request_validator, mock_gr_sensitive_data_repository):
    """Test updating an existing GRSensitiveData."""
    mock_request = GRSensitiveDataView(name="Updated Data", label="Updated Label", guardrail_provider="AWS")

    mock_gr_sensitive_data_repository.list_records.return_value = ([], 0)
    mock_gr_sensitive_data_repository.update_record.return_value = GRSensitiveDataModel(id=1, name="Updated Data", label="Updated Label", guardrail_provider="AWS")

    result = await service.update_gr_sensitive_data(1, mock_request)
    assert result.name == "Updated Data"
    assert result.label == "Updated Label"
    assert result.guardrail_provider == "AWS"

@pytest.mark.asyncio
async def test_delete_gr_sensitive_data(service, request_validator, mock_gr_sensitive_data_repository):
    """Test deleting a GRSensitiveData."""
    gr_sensitive_data_model = GRSensitiveDataModel(id=1, name="Test Data", label="Test Label", guardrail_provider="AWS")

    mock_gr_sensitive_data_repository.get_record_by_id.return_value = gr_sensitive_data_model
    mock_gr_sensitive_data_repository.delete_record.return_value = None

    await service.delete_gr_sensitive_data(1)
    mock_gr_sensitive_data_repository.delete_record.assert_called_once_with(gr_sensitive_data_model)

@pytest.mark.asyncio
async def test_list_gr_sensitive_datas(service, mock_gr_sensitive_data_repository):
    """Test listing GRSensitiveData with filtering, pagination, and sorting."""
    mock_filter = GRSensitiveDataFilter(name="Test Data")

    mock_gr_sensitive_data_repository.list_records.return_value = ([GRSensitiveDataModel(id=1, name="Test Data", label="Test Label", guardrail_provider="AWS")], 1)

    result = await service.list_gr_sensitive_datas(mock_filter, 1, 10, ["id"])
    assert len(result.content) == 1
    assert result.content[0].name == "Test Data"

@pytest.mark.asyncio
async def test_get_gr_sensitive_data_by_id(service, mock_gr_sensitive_data_repository):
    """Test retrieving a GRSensitiveData by ID."""
    mock_gr_sensitive_data_repository.get_record_by_id.return_value = GRSensitiveDataModel(id=1, name="Test Data", label="Test Label", guardrail_provider="AWS")

    result = await service.get_gr_sensitive_data_by_id(1)
    assert result.name == "Test Data"
    assert result.label == "Test Label"
    assert result.guardrail_provider == "AWS"