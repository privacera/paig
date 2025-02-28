import pytest
from unittest.mock import patch
from sqlalchemy.exc import NoResultFound

from api.guardrails.database.db_models.response_template_model import ResponseTemplateModel
from api.guardrails.database.db_operations.response_template_repository import ResponseTemplateRepository


@pytest.fixture
def mock_response_template_repository():
    return ResponseTemplateRepository()


@pytest.mark.asyncio
async def test_get_response_templates(mock_response_template_repository):
    mock_template = ResponseTemplateModel(
        id=1,
        response="Sample response",
        description="Sample description"
    )

    with patch.object(ResponseTemplateRepository, 'get_all', return_value=[mock_template]):
        result = await mock_response_template_repository.get_all()
        assert len(result) == 1
        assert result[0].response == "Sample response"
        assert result[0].description == "Sample description"


@pytest.mark.asyncio
async def test_get_response_template_by_id(mock_response_template_repository):
    template_id = 1
    mock_template = ResponseTemplateModel(
        id=template_id,
        response="Sample response",
        description="Sample description"
    )

    with patch.object(ResponseTemplateRepository, 'get_record_by_id', return_value=mock_template):
        result = await mock_response_template_repository.get_record_by_id(template_id)
        assert result.id == template_id
        assert result.response == "Sample response"
        assert result.description == "Sample description"


@pytest.mark.asyncio
async def test_get_response_template_by_id_not_found(mock_response_template_repository):
    template_id = 0

    with patch.object(ResponseTemplateRepository, 'get_record_by_id', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_response_template_repository.get_record_by_id(template_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_create_response_template(mock_response_template_repository):
    mock_template = ResponseTemplateModel(
        id=1,
        response="Sample response",
        description="Sample description"
    )

    with patch.object(ResponseTemplateRepository, 'create', return_value=mock_template):
        result = await mock_response_template_repository.create(mock_template)
        assert result.id == 1
        assert result.response == "Sample response"
        assert result.description == "Sample description"


@pytest.mark.asyncio
async def test_update_response_template(mock_response_template_repository):
    template_id = 1
    mock_template = ResponseTemplateModel(
        id=template_id,
        response="Updated response",
        description="Updated description"
    )

    with patch.object(ResponseTemplateRepository, 'update', return_value=mock_template):
        result = await mock_response_template_repository.update(mock_template)
        assert result.id == template_id
        assert result.response == "Updated response"
        assert result.description == "Updated description"


@pytest.mark.asyncio
async def test_delete_response_template(mock_response_template_repository):
    template_id = 1
    mock_template = ResponseTemplateModel(
        id=template_id,
        response="Sample response",
        description="Sample description"
    )

    with patch.object(ResponseTemplateRepository, 'delete', return_value=None):
        result = await mock_response_template_repository.delete(mock_template)
        assert result is None
