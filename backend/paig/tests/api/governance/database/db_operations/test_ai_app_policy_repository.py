import pytest
from unittest.mock import AsyncMock
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel
from api.governance.database.db_operations.ai_app_policy_repository import AIAppPolicyRepository


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

    query_mock = AsyncMock()
    query_mock.filter.return_value = query_mock
    ai_app_policy_repository._query = AsyncMock(return_value=query_mock)
    ai_app_policy_repository._all = AsyncMock(return_value=[policy])

    result = await ai_app_policy_repository.list_policies_for_authorization(application_id, tags, user, groups)

    assert result == [policy]
    ai_app_policy_repository._query.assert_called_once()
    query_mock.filter.assert_called_once()


@pytest.mark.asyncio
async def test_list_policies_for_authorization_no_policies(ai_app_policy_repository):
    application_id = 1
    tags = ["tag1", "tag2"]
    user = "user1"
    groups = ["group1", "group2"]

    query_mock = AsyncMock()
    query_mock.filter.return_value = query_mock
    ai_app_policy_repository._query = AsyncMock(return_value=query_mock)
    ai_app_policy_repository._all = AsyncMock(return_value=[])

    result = await ai_app_policy_repository.list_policies_for_authorization(application_id, tags, user, groups)

    assert result == []
    ai_app_policy_repository._query.assert_called_once()
    query_mock.filter.assert_called_once()
