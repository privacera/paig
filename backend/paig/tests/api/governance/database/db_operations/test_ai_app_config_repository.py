import pytest
from unittest.mock import AsyncMock

from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel
from api.governance.database.db_operations.ai_app_config_repository import AIAppConfigRepository


@pytest.fixture
def ai_app_config_repository():
    return AIAppConfigRepository()


@pytest.mark.asyncio
async def test_get_ai_app_config_by_ai_application_id_found(ai_app_config_repository):
    application_id = 1
    ai_app_config = AIApplicationConfigModel(application_id=application_id)

    # Mock the list_records method to return a list with the ai_app_config and a total count
    ai_app_config_repository.list_records = AsyncMock(return_value=([ai_app_config], 1))

    result = await ai_app_config_repository.get_ai_app_config_by_ai_application_id(application_id)

    assert result == ai_app_config
    ai_app_config_repository.list_records.assert_called_once()


@pytest.mark.asyncio
async def test_get_ai_app_config_by_ai_application_id_not_found(ai_app_config_repository):
    application_id = 1

    # Mock the list_records method to return an empty list and a total count of 0
    ai_app_config_repository.list_records = AsyncMock(return_value=([], 0))

    result = await ai_app_config_repository.get_ai_app_config_by_ai_application_id(application_id)

    assert result is None
    ai_app_config_repository.list_records.assert_called_once()
