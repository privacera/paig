import pytest
from unittest.mock import AsyncMock

from core.exceptions import BadRequestException
from api.guardrails.api_schemas.response_template import ResponseTemplateView, ResponseTemplateFilter
from api.guardrails.database.db_models.response_template_model import ResponseTemplateModel
from api.guardrails.database.db_operations.response_template_repository import ResponseTemplateRepository
from api.guardrails.services.response_template_service import ResponseTemplateRequestValidator, ResponseTemplateService

@pytest.fixture
def mock_response_template_repository():
    """Fixture for mocking the ResponseTemplateRepository."""
    return AsyncMock(spec=ResponseTemplateRepository)

@pytest.fixture
def request_validator(mock_response_template_repository):
    """Fixture for initializing the ResponseTemplateRequestValidator."""
    return ResponseTemplateRequestValidator(response_template_repository=mock_response_template_repository)

@pytest.fixture
def service(mock_response_template_repository, request_validator):
    """Fixture for initializing the ResponseTemplateService."""
    return ResponseTemplateService(
        response_template_repository=mock_response_template_repository,
        response_template_request_validator=request_validator
    )

@pytest.mark.asyncio
async def test_validate_create_request(request_validator, mock_response_template_repository):
    """Test the create request validation."""
    mock_request = ResponseTemplateView(response="Test Response", description="Test Description")
    mock_response_template_repository.list_records.return_value = ([], 0)

    await request_validator.validate_create_request(mock_request)
    mock_response_template_repository.list_records.assert_called_once()

@pytest.mark.asyncio
async def test_validate_create_request_existing_response(request_validator, mock_response_template_repository):
    """Test create request validation when the response template already exists."""
    mock_request = ResponseTemplateView(response="Test Response", description="Test Description")
    existing_template = ResponseTemplateModel(id=1, response="Test Response", description="Existing")
    mock_response_template_repository.list_records.return_value = ([existing_template], 1)

    with pytest.raises(BadRequestException):
        await request_validator.validate_create_request(mock_request)

@pytest.mark.asyncio
async def test_list_response_templates(service, mock_response_template_repository):
    """Test listing response templates with filtering, pagination, and sorting."""
    mock_filter = ResponseTemplateFilter(response="Test Response")

    mock_response_template_repository.list_records.return_value = ([ResponseTemplateModel(id=1, response="Test Response", description="Test")], 1)

    result = await service.list_response_templates(mock_filter, 1, 10, ["id"])
    assert len(result.content) == 1
    assert result.content[0].response == "Test Response"

@pytest.mark.asyncio
async def test_create_response_template(service, request_validator, mock_response_template_repository):
    """Test creating a new response template."""
    mock_request = ResponseTemplateView(response="New Response", description="New Description")

    mock_response_template_repository.list_records.return_value = ([], 0)
    mock_response_template_repository.create_record.return_value = ResponseTemplateModel(id=1, response="New Response", description="New Description")

    result = await service.create_response_template(mock_request)
    assert result.response == "New Response"
    assert result.description == "New Description"

@pytest.mark.asyncio
async def test_update_response_template(service, request_validator, mock_response_template_repository):
    """Test updating an existing response template."""
    mock_request = ResponseTemplateView(response="Updated Response", description="Updated Description")

    mock_response_template_repository.list_records.return_value = ([], 0)
    mock_response_template_repository.update_record.return_value = ResponseTemplateModel(id=1, response="Updated Response", description="Updated Description")

    result = await service.update_response_template(1, mock_request)
    assert result.response == "Updated Response"
    assert result.description == "Updated Description"

@pytest.mark.asyncio
async def test_delete_response_template(service, request_validator, mock_response_template_repository):
    """Test deleting a response template."""
    response_template_model = ResponseTemplateModel(id=1, response="Test Response", description="Test Description")

    mock_response_template_repository.get_record_by_id.return_value = response_template_model
    mock_response_template_repository.delete.return_value = None

    await service.delete_response_template(1)
    mock_response_template_repository.delete_record.assert_called_once_with(response_template_model)
