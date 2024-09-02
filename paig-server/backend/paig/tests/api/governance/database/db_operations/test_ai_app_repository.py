import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import NoResultFound
from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel
from core.exceptions import NotFoundException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from api.governance.database.db_models.ai_app_model import AIApplicationModel
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel
from api.governance.database.db_operations.ai_app_repository import AIAppRepository


@pytest.fixture
def ai_app_repository():
    return AIAppRepository()

@pytest.fixture
def new_ai_app_repository(db_session, set_context_session):
    return AIAppRepository()


@pytest.mark.asyncio
async def test_get_ai_application_by_application_key_found(ai_app_repository):
    application_key = "test_app_key"
    ai_application = AIApplicationModel(application_key=application_key)

    # Mock the get_by method to return the ai_application
    with patch("api.governance.database.db_operations.ai_app_repository.AIAppRepository.get_by",
               new_callable=AsyncMock, return_value=ai_application):

        result = await ai_app_repository.get_ai_application_by_application_key(application_key)

        assert result == ai_application


@pytest.mark.asyncio
async def test_get_ai_application_by_application_key_not_found(ai_app_repository):
    application_key = "nonexistent_app_key"

    # Mock the get_by method to raise NoResultFound
    with patch("api.governance.database.db_operations.ai_app_repository.AIAppRepository.get_by",
               new_callable=AsyncMock, side_effect=NoResultFound):
        with pytest.raises(NotFoundException) as exc_info:
            await ai_app_repository.get_ai_application_by_application_key(application_key)

        assert str(exc_info.value) == get_error_message(ERROR_RESOURCE_NOT_FOUND, "AI Application", "applicationKey",
                                                        application_key)
