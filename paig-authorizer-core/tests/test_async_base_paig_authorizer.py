import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, Mock
from typing import List

from paig_authorizer_core.async_base_paig_authorizer import AsyncBasePAIGAuthorizer
from paig_authorizer_core.constants import PermissionType, VectorDBType
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.data_models import AIApplicationData
from paig_authorizer_core.models.data_models import AIApplicationConfigData
from paig_authorizer_core.models.data_models import AIApplicationPolicyData
from paig_authorizer_core.models.data_models import VectorDBData
from paig_authorizer_core.models.data_models import VectorDBPolicyData
from paig_authorizer_core.filter.base_metadata_filter_criteria_creator import BaseMetadataFilterCriteriaCreator
from paig_authorizer_core.filter.snowflake_cortex_metadata_filter_creator import SnowflakeCortexMetadataFilterCreator


class AsyncMockPAIGAuthorizer(AsyncBasePAIGAuthorizer):
    async def get_user_id_by_email(self, email: str) -> str | None:
        return "test_user"

    async def get_user_groups(self, user: str) -> List[str]:
        return ["group1"]

    async def get_application_details(self, application_key: str, **kwargs) -> AIApplicationData:
        return AIApplicationData(id=1, name="TestApp", status=1, vector_dbs=["TestDB"], vector_db_id=1, vector_db_name="TestDB")

    async def get_application_config(self, application_key: str, **kwargs) -> AIApplicationConfigData:
        return AIApplicationConfigData(id=1, allowed_users=["test_user"], allowed_groups=["group1"])

    async def get_application_policies(self, application_key: str, traits: List[str], user: str, groups: List[str],
                                       request_type: str, **kwargs) -> List[AIApplicationPolicyData]:
        trait1_policy = AIApplicationPolicyData(
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

        trait2_policy = AIApplicationPolicyData(
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

    async def get_vector_db_details(self, vector_db_id: int, **kwargs) -> VectorDBData:
        return VectorDBData(id=1, name="TestDB", type=VectorDBType.MILVUS, status=1)

    async def get_vector_db_policies(self, vector_db_id: int, user: str, groups: List[str], **kwargs) \
            -> List[VectorDBPolicyData]:
        return [VectorDBPolicyData(
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
    authorizer = AsyncMockPAIGAuthorizer()
    return authorizer


@pytest.mark.asyncio
async def test_authorize_success(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    authz_request.traits = ["trait1"]
    response = await authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.masked_traits == {}
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_authorize_app_disabled(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    authorizer.get_application_details = AsyncMock(
        return_value=AIApplicationData(id=1, name="TestApp", status=0, vector_dbs=["TestDB"]))
    response = await authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert response.reason == "Application is disabled"


@pytest.mark.asyncio
async def test_authorize_vector_db_success(vector_db_authz_request, authorizer: AsyncBasePAIGAuthorizer):
    response = await authorizer.authorize_vector_db(vector_db_authz_request)

    assert response.vector_db_id == 1
    assert response.vector_db_name == "TestDB"
    assert response.filter_expression is not None


@pytest.mark.asyncio
async def test_authorize_vector_db_disabled(vector_db_authz_request, authorizer: AsyncBasePAIGAuthorizer):
    authorizer.get_vector_db_details = AsyncMock(
        return_value=VectorDBData(id=1, name="TestDB", type=VectorDBType.MILVUS, status=0))
    response = await authorizer.authorize_vector_db(vector_db_authz_request)

    assert response.vector_db_id == 1
    assert response.vector_db_name == "TestDB"
    assert response.reason == "Vector DB is disabled"


@pytest.mark.asyncio
async def test_authorize_no_matching_policies(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    authorizer.get_application_policies = AsyncMock(return_value=[])
    response = await authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_authorize_explicit_deny(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    authz_request.traits = ["trait2"]
    response = await authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert 2 in response.paig_policy_ids


@pytest.mark.asyncio
async def test_authorize_application_config_explicit_user_allow(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    app_config = AIApplicationConfigData(id=1, allowed_users=["test_user"])
    authorizer.get_application_config = AsyncMock(return_value=app_config)
    authorizer.get_application_policies = AsyncMock(return_value=[])
    response = await authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.status_code == 200
    assert 1 in response.paig_policy_ids

@pytest.mark.asyncio
async def test_authorize_application_config_explicit_group_allow(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    app_config = AIApplicationConfigData(id=1, allowed_groups=["public"])
    authorizer.get_application_config = AsyncMock(return_value=app_config)
    authorizer.get_application_policies = AsyncMock(return_value=[])
    response = await authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.status_code == 200
    assert 1 in response.paig_policy_ids

@pytest.mark.asyncio
async def test_authorize_application_config_explicit_user_deny(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    app_config = AIApplicationConfigData(id=1, denied_users=["test_user"])
    authorizer.get_application_config = AsyncMock(return_value=app_config)
    authorizer.get_application_policies = AsyncMock(return_value=[])
    response = await authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert 1 in response.paig_policy_ids
    assert response.reason == "Explicit deny access to Application"

@pytest.mark.asyncio
async def test_authorize_application_config_explicit_group_deny(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    app_config = AIApplicationConfigData(id=1, denied_groups=["public"])
    authorizer.get_application_config = AsyncMock(return_value=app_config)
    authorizer.get_application_policies = AsyncMock(return_value=[])
    response = await authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert 1 in response.paig_policy_ids
    assert response.reason == "Explicit deny access to Application"

@pytest.mark.asyncio
async def test_authorize_application_config_no_access(authz_request, authorizer: AsyncBasePAIGAuthorizer):
    app_config = AIApplicationConfigData(id=1)
    authorizer.get_application_config = AsyncMock(return_value=app_config)
    authorizer.get_application_policies = AsyncMock(return_value=[])
    response = await authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert 1 in response.paig_policy_ids
    assert response.reason == "No Access to Application"


# Tests for metadata filter creator
def test_get_metadata_filter_creator_snowflake_cortex(authorizer):
    """Test that SnowflakeCortexMetadataFilterCreator is returned for SNOWFLAKE_CORTEX type"""
    filter_creator = authorizer.get_metadata_filter_creator(VectorDBType.SNOWFLAKE_CORTEX)
    assert isinstance(filter_creator, SnowflakeCortexMetadataFilterCreator)


def test_get_metadata_filter_creator_other_types(authorizer):
    """Test that BaseMetadataFilterCriteriaCreator is returned for other vector DB types"""
    # Test with MILVUS
    filter_creator = authorizer.get_metadata_filter_creator(VectorDBType.MILVUS)
    assert isinstance(filter_creator, BaseMetadataFilterCriteriaCreator)
    assert not isinstance(filter_creator, SnowflakeCortexMetadataFilterCreator)

    # Test with OPENSEARCH
    filter_creator = authorizer.get_metadata_filter_creator(VectorDBType.OPENSEARCH)
    assert isinstance(filter_creator, BaseMetadataFilterCriteriaCreator)
    assert not isinstance(filter_creator, SnowflakeCortexMetadataFilterCreator)


@pytest.mark.asyncio
async def test_authorize_vector_db_uses_correct_filter_creator(authorizer, monkeypatch):
    """Test that authorize_vector_db uses the correct filter creator based on vector DB type"""
    # Mock vector DB with SNOWFLAKE_CORTEX type
    mock_vector_db = Mock(spec=VectorDBData)
    mock_vector_db.type = VectorDBType.SNOWFLAKE_CORTEX
    mock_vector_db.status = 1

    # Mock get_vector_db_details to return our mock
    async def mock_get_vector_db_details(self, vector_db_id, **kwargs):
        return mock_vector_db

    monkeypatch.setattr(AsyncMockPAIGAuthorizer, "get_vector_db_details", mock_get_vector_db_details)

    # Mock the filter creator methods
    calls = []
    original_get_metadata_filter_creator = authorizer.get_metadata_filter_creator

    def mock_get_metadata_filter_creator(vector_db_type):
        calls.append(vector_db_type)
        return original_get_metadata_filter_creator(vector_db_type)

    monkeypatch.setattr(authorizer, "get_metadata_filter_creator", mock_get_metadata_filter_creator)

    # Create a mock request
    mock_request = Mock(spec=VectorDBAuthzRequest)
    mock_request.user_id = "test_user"
    mock_request.application_key = "TestApp"

    # Call authorize_vector_db
    await authorizer.authorize_vector_db(mock_request)

    # Check that get_metadata_filter_creator was called with SNOWFLAKE_CORTEX
    assert VectorDBType.SNOWFLAKE_CORTEX in calls