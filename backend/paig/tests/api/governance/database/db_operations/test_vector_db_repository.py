import pytest
from unittest.mock import AsyncMock
from sqlalchemy.exc import NoResultFound

from core.exceptions import NotFoundException
from api.governance.database.db_models.vector_db_model import VectorDBModel
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from api.governance.database.db_operations.vector_db_repository import VectorDBRepository
from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel


@pytest.fixture
def vector_db_repository():
    return VectorDBRepository()


@pytest.mark.asyncio
async def test_get_vector_db_by_name_success(vector_db_repository):
    vector_db_name = "example_db"
    vector_db = VectorDBModel(name=vector_db_name)

    vector_db_repository.get_by = AsyncMock(return_value=vector_db)

    result = await vector_db_repository.get_vector_db_by_name(vector_db_name)

    assert result == vector_db
    vector_db_repository.get_by.assert_called_once_with(filters={"name": vector_db_name}, unique=True)


@pytest.mark.asyncio
async def test_get_vector_db_by_name_not_found(vector_db_repository):
    vector_db_name = "nonexistent_db"

    vector_db_repository.get_by = AsyncMock(side_effect=NoResultFound)

    with pytest.raises(NotFoundException) as excinfo:
        await vector_db_repository.get_vector_db_by_name(vector_db_name)

    assert str(excinfo.value) == get_error_message(ERROR_RESOURCE_NOT_FOUND, "Vector DB", "name", vector_db_name)
    vector_db_repository.get_by.assert_called_once_with(filters={"name": vector_db_name}, unique=True)
