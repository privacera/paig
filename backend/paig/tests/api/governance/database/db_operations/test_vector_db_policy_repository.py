import pytest
from unittest.mock import AsyncMock, patch
from api.governance.database.db_models.vector_db_policy_model import VectorDBPolicyModel
from api.governance.database.db_operations.vector_db_policy_repository import VectorDBPolicyRepository
from api.governance.database.db_models.ai_app_config_model import AIApplicationConfigModel
from api.governance.database.db_models.ai_app_policy_model import AIApplicationPolicyModel


@pytest.fixture
def vector_db_policy_repository():
    return VectorDBPolicyRepository()


@pytest.mark.asyncio
async def list_policies_for_authorization_success(vector_db_policy_repository):
    vector_db_id = 1
    user = "test_user"
    groups = ["group1", "group2"]

    mock_policies = [
        VectorDBPolicyModel(id=1, vector_db_id=vector_db_id, status=1, allowed_users="test_user", denied_users="",
                            allowed_groups="group1", denied_groups=""),
        VectorDBPolicyModel(id=2, vector_db_id=vector_db_id, status=1, allowed_users="", denied_users="",
                            allowed_groups="group2", denied_groups="")
    ]

    with patch("api.governance.database.db_operations.vector_db_policy_repository.VectorDBPolicyRepository._all",
               new_callable=AsyncMock, return_value=mock_policies):
        policies = await vector_db_policy_repository.list_policies_for_authorization(vector_db_id, user, groups)

        assert len(policies) == len(mock_policies)
        assert policies == mock_policies


@pytest.mark.asyncio
async def test_list_policies_for_authorization_no_policies(vector_db_policy_repository):
    vector_db_id = 1
    user = "test_user"
    groups = ["group1", "group2"]

    with patch("api.governance.database.db_operations.vector_db_policy_repository.VectorDBPolicyRepository._all",
               new_callable=AsyncMock, return_value=[]):
        policies = await vector_db_policy_repository.list_policies_for_authorization(vector_db_id, user, groups)

        assert len(policies) == 0
        assert policies == []
