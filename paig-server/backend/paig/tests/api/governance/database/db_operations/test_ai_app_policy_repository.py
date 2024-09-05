import pytest
from unittest.mock import AsyncMock, patch
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel
from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel
from api.governance.database.db_operations.ai_app_policy_repository import AIAppPolicyRepository
from api.governance.database.db_models.ai_app_model import AIApplicationModel


@pytest.fixture
def ai_app_policy_repository():
    return AIAppPolicyRepository()


@pytest.mark.asyncio
async def test_list_policies_for_authorization(ai_app_policy_repository):
    application_id = 1
    tags = ["tag1", "tag2"]
    user = "user1"
    groups = ["group1", "group2"]

    policy = AIApplicationPolicyModel(
        application_id=application_id,
        status=1,
        tags="tag1,tag2",
        users="user1",
        groups="group1,group2"
    )

    with patch("api.governance.database.db_operations.ai_app_policy_repository.AIAppPolicyRepository._all",
               new_callable=AsyncMock, return_value=[policy]):
        result = await ai_app_policy_repository.list_policies_for_authorization(application_id, tags, user, groups)

        assert result == [policy]


@pytest.mark.asyncio
async def test_list_policies_for_authorization_no_policies(ai_app_policy_repository):
    application_id = 1
    tags = ["tag1", "tag2"]
    user = "user1"
    groups = ["group1", "group2"]

    with patch("api.governance.database.db_operations.ai_app_policy_repository.AIAppPolicyRepository._all",
               new_callable=AsyncMock, return_value=[]):
        result = await ai_app_policy_repository.list_policies_for_authorization(application_id, tags, user, groups)

        assert result == []
