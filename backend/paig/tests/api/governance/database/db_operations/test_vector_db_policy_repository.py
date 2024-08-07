import pytest
from unittest.mock import AsyncMock
from api.governance.database.db_models.vector_db_policy_model import VectorDBPolicyModel
from api.governance.database.db_operations.vector_db_policy_repository import VectorDBPolicyRepository


@pytest.fixture
def vector_db_policy_repository():
    return VectorDBPolicyRepository()


@pytest.mark.asyncio
async def test_list_policies_for_authorization_success(vector_db_policy_repository):
    vector_db_id = 1
    user = "test_user"
    groups = ["group1", "group2"]

    mock_policies = [
        VectorDBPolicyModel(id=1, vector_db_id=vector_db_id, status=1, allowed_users="test_user", denied_users="",
                            allowed_groups="group1", denied_groups=""),
        VectorDBPolicyModel(id=2, vector_db_id=vector_db_id, status=1, allowed_users="", denied_users="",
                            allowed_groups="group2", denied_groups="")
    ]

    query_mock = AsyncMock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = mock_policies
    vector_db_policy_repository._query = AsyncMock(return_value=query_mock)
    vector_db_policy_repository._all = AsyncMock(return_value=mock_policies)

    policies = await vector_db_policy_repository.list_policies_for_authorization(vector_db_id, user, groups)

    assert len(policies) == len(mock_policies)
    assert policies == mock_policies
    vector_db_policy_repository._query.assert_called_once()
    vector_db_policy_repository._all.assert_called_once()


@pytest.mark.asyncio
async def test_list_policies_for_authorization_no_policies(vector_db_policy_repository):
    vector_db_id = 1
    user = "test_user"
    groups = ["group1", "group2"]

    query_mock = AsyncMock()
    query_mock.filter.return_value = query_mock
    query_mock.all.return_value = []
    vector_db_policy_repository._query = AsyncMock(return_value=query_mock)
    vector_db_policy_repository._all = AsyncMock(return_value=[])

    policies = await vector_db_policy_repository.list_policies_for_authorization(vector_db_id, user, groups)

    assert len(policies) == 0
    assert policies == []
    vector_db_policy_repository._query.assert_called_once()
    vector_db_policy_repository._all.assert_called_once()