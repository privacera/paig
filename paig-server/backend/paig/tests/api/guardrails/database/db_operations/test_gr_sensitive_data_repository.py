from unittest.mock import patch
import pytest
from sqlalchemy.exc import NoResultFound

from api.guardrails.database.db_models.gr_sensitive_data_model import GRSensitiveDataModel
from api.guardrails.database.db_operations.gr_sensitive_data_repository import GRSensitiveDataRepository
from api.guardrails import GuardrailProvider


@pytest.fixture
def mock_gr_sensitive_data_repository():
    return GRSensitiveDataRepository()


@pytest.mark.asyncio
async def test_create_gr_sensitive_data(mock_gr_sensitive_data_repository):
    mock_gr_sensitive_data = GRSensitiveDataModel(
        name="Name",
        label="NAME",
        guardrail_provider=GuardrailProvider.AWS,
        description="Name of the person"
    )

    with patch.object(GRSensitiveDataRepository, 'create', return_value=mock_gr_sensitive_data):
        result = await mock_gr_sensitive_data_repository.create(mock_gr_sensitive_data)
        assert result.name == "Name"
        assert result.label == "NAME"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.description == "Name of the person"


@pytest.mark.asyncio
async def test_get_gr_sensitive_data_by_id(mock_gr_sensitive_data_repository):
    key_id = 1
    mock_gr_sensitive_data = GRSensitiveDataModel(
        id=key_id,
        name="Name",
        label="NAME",
        guardrail_provider=GuardrailProvider.AWS,
        description="Name of the person"
    )

    with patch.object(GRSensitiveDataRepository, 'get_record_by_id', return_value=mock_gr_sensitive_data):
        result = await mock_gr_sensitive_data_repository.get_record_by_id(key_id)
        assert result.id == key_id
        assert result.name == "Name"
        assert result.label == "NAME"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.description == "Name of the person"


@pytest.mark.asyncio
async def test_get_gr_sensitive_data_by_id_not_found(mock_gr_sensitive_data_repository):
    key_id = 0

    with patch.object(GRSensitiveDataRepository, 'get_record_by_id', side_effect=NoResultFound):
        with pytest.raises(NoResultFound) as exc_info:
            await mock_gr_sensitive_data_repository.get_record_by_id(key_id)

        assert exc_info.type == NoResultFound


@pytest.mark.asyncio
async def test_update_gr_sensitive_data(mock_gr_sensitive_data_repository):
    key_id = 1
    mock_gr_sensitive_data = GRSensitiveDataModel(
        id=key_id,
        name="Updated Name",
        label="UPDATED_NAME",
        guardrail_provider=GuardrailProvider.AWS,
        description="Updated description"
    )

    with patch.object(GRSensitiveDataRepository, 'update', return_value=mock_gr_sensitive_data):
        result = await mock_gr_sensitive_data_repository.update(mock_gr_sensitive_data)
        assert result.id == key_id
        assert result.name == "Updated Name"
        assert result.label == "UPDATED_NAME"
        assert result.guardrail_provider == GuardrailProvider.AWS
        assert result.description == "Updated description"


@pytest.mark.asyncio
async def test_delete_gr_sensitive_data(mock_gr_sensitive_data_repository):
    key_id = 1
    mock_gr_sensitive_data = GRSensitiveDataModel(
        id=key_id,
        name="Name",
        label="NAME",
        guardrail_provider=GuardrailProvider.AWS,
        description="Name of the person"
    )

    with patch.object(GRSensitiveDataRepository, 'delete', return_value=None):
        result = await mock_gr_sensitive_data_repository.delete(mock_gr_sensitive_data)
        assert result is None


@pytest.mark.asyncio
async def test_get_all_gr_sensitive_data(mock_gr_sensitive_data_repository):
    mock_gr_sensitive_data = GRSensitiveDataModel(
        name="Name",
        label="NAME",
        guardrail_provider=GuardrailProvider.AWS,
        description="Name of the person"
    )

    with patch.object(GRSensitiveDataRepository, 'get_all', return_value=[mock_gr_sensitive_data]):
        result = await mock_gr_sensitive_data_repository.get_all()
        assert len(result) == 1
        assert result[0].name == "Name"
        assert result[0].label == "NAME"
        assert result[0].guardrail_provider == GuardrailProvider.AWS
        assert result[0].description == "Name of the person"
