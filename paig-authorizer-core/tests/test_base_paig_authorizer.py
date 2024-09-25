import pytest
from unittest.mock import Mock
from typing import List

from paig_authorizer_core.base_paig_authorizer import BasePAIGAuthorizer
from paig_authorizer_core.constants import PermissionType, VectorDBType
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.data_models import AIApplicationData
from paig_authorizer_core.models.data_models import AIApplicationConfigData
from paig_authorizer_core.models.data_models import AIApplicationPolicyData
from paig_authorizer_core.models.data_models import VectorDBData
from paig_authorizer_core.models.data_models import VectorDBPolicyData


class MockPAIGAuthorizer(BasePAIGAuthorizer):

    def get_user_id_by_email(self, email: str) -> str | None:
        return "test_user"

    def get_user_groups(self, user: str) -> List[str]:
        return ["group1"]

    def get_application_details(self, application_key: str, **kwargs) -> AIApplicationData:
        return AIApplicationData(id=1, name="TestApp", status=1, vector_dbs=["TestDB"], vector_db_id=1, vector_db_name="TestDB")

    def get_application_config(self, application_key: str, **kwargs) -> AIApplicationConfigData:
        return AIApplicationConfigData(id=1, allowed_users=["test_user"], allowed_groups=["group1"])

    def get_application_policies(self, application_key: str, traits: List[str], user: str, groups: List[str],
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

    def get_vector_db_details(self, vector_db_id: int, **kwargs) -> VectorDBData:
        return VectorDBData(id=1, name="TestDB", type=VectorDBType.MILVUS, status=1)

    def get_vector_db_policies(self, vector_db_id: int, user: str, groups: List[str], **kwargs) \
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


@pytest.fixture
def authorizer():
    authorizer = MockPAIGAuthorizer()
    return authorizer


def test_authorize_success(authz_request, authorizer: BasePAIGAuthorizer):
    authz_request.traits = ["trait1"]
    response = authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.masked_traits == {}
    assert response.status_code == 200


def test_authorize_app_disabled(authz_request, authorizer: BasePAIGAuthorizer):
    authorizer.get_application_details = Mock(
        return_value=AIApplicationData(id=1, name="TestApp", status=0, vector_dbs=["TestDB"]))
    response = authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert response.reason == "Application is disabled"


def test_authorize_vector_db_success(vector_db_authz_request, authorizer: BasePAIGAuthorizer):
    response = authorizer.authorize_vector_db(vector_db_authz_request)

    assert response.vector_db_id == 1
    assert response.vector_db_name == "TestDB"
    assert response.filter_expression is not None


def test_authorize_vector_db_disabled(vector_db_authz_request, authorizer: BasePAIGAuthorizer):
    authorizer.get_vector_db_details = Mock(
        return_value=VectorDBData(id=1, name="TestDB", type=VectorDBType.MILVUS, status=0))
    response = authorizer.authorize_vector_db(vector_db_authz_request)

    assert response.vector_db_id == 1
    assert response.vector_db_name == "TestDB"
    assert response.reason == "Vector DB is disabled"


def test_authorize_no_matching_policies(authz_request, authorizer: BasePAIGAuthorizer):
    authorizer.get_application_policies = Mock(return_value=[])
    response = authorizer.authorize(authz_request)

    assert response.authorized is True
    assert response.status_code == 200


def test_authorize_explicit_deny(authz_request, authorizer: BasePAIGAuthorizer):
    authz_request.traits = ["trait2"]
    response = authorizer.authorize(authz_request)

    assert response.authorized is False
    assert response.status_code == 403
    assert 2 in response.paig_policy_ids
