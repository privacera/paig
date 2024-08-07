import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from typing import List

from api.authz.authorizer.base_paig_authorizer import BasePAIGAuthorizer
from api.authz.authorizer.paig_authorizer import AuthzRequest, VectorDBAuthzRequest
from api.governance.api_schemas.ai_app import AIApplicationView
from api.governance.api_schemas.ai_app_config import AIApplicationConfigView
from api.governance.api_schemas.ai_app_policy import AIApplicationPolicyView
from api.governance.api_schemas.vector_db import VectorDBView
from api.governance.api_schemas.vector_db_policy import VectorDBPolicyView
from api.governance.database.db_models.ai_app_policy_model import PermissionType
from api.governance.database.db_models.vector_db_model import VectorDBType


class MockPAIGAuthorizer(BasePAIGAuthorizer):
    async def get_user_groups(self, user: str) -> List[str]:
        return ["group1"]

    async def get_application_details(self, application_key: str, **kwargs) -> AIApplicationView:
        return AIApplicationView(id=1, name="TestApp", status=1, vector_dbs=["TestDB"])

    async def get_application_config(self, application_key: str, **kwargs) -> AIApplicationConfigView:
        return AIApplicationConfigView(id=1, allowed_users=["test_user"], allowed_groups=["group1"])

    async def get_application_policies(self, application_key: str, traits: List[str], user: str, groups: List[str],
                                       request_type: str, **kwargs) -> List[AIApplicationPolicyView]:
        trait1_policy = AIApplicationPolicyView(
            id=1,
            tags=["trait1"],
            description="Policy 1",
            users=["test_user"],
            groups=["group1"],
            roles=["role1"],
            prompt=PermissionType.ALLOW,
            reply=PermissionType.ALLOW,
            enriched_prompt=PermissionType.ALLOW,
        )

        trait2_policy = AIApplicationPolicyView(
            id=2,
            read=PermissionType.DENY,
            tags=["tag2"],
            description="Policy 2",
            users=["test_user"],
            groups=["group1"],
            roles=["role1"],
            prompt=PermissionType.DENY,
            reply=PermissionType.ALLOW,
            enriched_prompt=PermissionType.ALLOW,
        )

        policies = []
        if "trait1" in traits:
            policies.append(trait1_policy)
        if "trait2" in traits:
            policies.append(trait2_policy)

        return policies

    async def get_vector_db_details(self, vector_db_name: str, **kwargs) -> VectorDBView:
        return VectorDBView(id=1, name="TestDB", type=VectorDBType.MILVUS, status=1)

    async def get_vector_db_policies(self, vector_db_id: int, user: str, groups: List[str], **kwargs) \
            -> List[VectorDBPolicyView]:
        return [VectorDBPolicyView(
            id=1,
            name="TestPolicy",
            description="Test policy",
            allowed_users=["test_user"],
            allowed_groups=["group1"],
            allowed_roles=["role1"],
            denied_users=[],
            denied_groups=[],
            denied_roles=[],
            metadata_key="key",
            metadata_value="value",
            operator="eq",
            vector_db_id=1
        )]


@pytest.fixture
def authz_request():
    request = AuthzRequest(
        request_id="1234",
        request_date_time="2024-07-10T10:00:00Z",
        user_id="test_user",
        context={"key": "value"},
        traits=["trait1", "trait2"],
        request_type="prompt"
    )
    request.request_type = "prompt"
    return request


@pytest.fixture
def vector_db_authz_request():
    return VectorDBAuthzRequest(
        user_id="test_user",
        application_key="TestApp"
    )


@pytest_asyncio.fixture
async def authorizer():
    authorizer = MockPAIGAuthorizer()
    return authorizer


@pytest.mark.asyncio
async def test_authorize_success(authz_request, authorizer: BasePAIGAuthorizer):
    authz_request.traits = ["trait1"]
    response = await authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.masked_traits == {}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_authorize_app_disabled(authz_request, authorizer: BasePAIGAuthorizer):
    authorizer.get_application_details = AsyncMock(
        return_value=AIApplicationView(id=1, name="TestApp", status=0, vector_dbs=["TestDB"]))
    response = await authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert response.reason == "Application is disabled"


@pytest.mark.asyncio
async def test_authorize_vector_db_success(vector_db_authz_request, authorizer: BasePAIGAuthorizer):
    response = await authorizer.authorize_vector_db(vector_db_authz_request)

    assert response.vector_db_id == 1
    assert response.vector_db_name == "TestDB"
    assert response.filter_expression is not None


@pytest.mark.asyncio
async def test_authorize_vector_db_disabled(vector_db_authz_request, authorizer: BasePAIGAuthorizer):
    authorizer.get_vector_db_details = AsyncMock(
        return_value=VectorDBView(id=1, name="TestDB", type=VectorDBType.MILVUS, status=0))
    response = await authorizer.authorize_vector_db(vector_db_authz_request)

    assert response.vector_db_id == 1
    assert response.vector_db_name == "TestDB"
    assert response.reason == "Vector DB is disabled"


@pytest.mark.asyncio
async def test_authorize_no_matching_policies(authz_request, authorizer: BasePAIGAuthorizer):
    authorizer.get_application_policies = AsyncMock(return_value=[])
    response = await authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_authorize_explicit_deny(authz_request, authorizer: BasePAIGAuthorizer):
    authz_request.traits = ["trait2"]
    response = await authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert 2 in response.paig_policy_ids
