import pytest
from datetime import datetime

from paig_authorizer_core.constants import VectorDBType
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from paig_authorizer_core.utils.authorizer_response_utils import create_authorize_response, \
    create_authorize_vector_db_response
from paig_authorizer_core.models.data_models import VectorDBData
from paig_authorizer_core.models.data_models import VectorDBPolicyData


@pytest.fixture
def authz_request():
    return AuthzRequest(
        request_id="1234",
        request_date_time=datetime.now(),
        user_id="test_user",
        context={"key": "value"}
    )


@pytest.fixture
def vector_db_authz_request():
    return VectorDBAuthzRequest(
        request_id="1234",
        request_date_time=datetime.now(),
        user_id="test_user",
        context={"key": "value"}
    )


@pytest.fixture
def vector_db_view():
    return VectorDBData(
        id=1,
        name="test_vector_db",
        type=VectorDBType.MILVUS,
        user_enforcement=1,
        group_enforcement=1
    )


@pytest.fixture
def vector_db_policy_view():
    return VectorDBPolicyData(
        id=1,
        policy_name="policy1",
        rules=[]
    )


def test_create_authorize_response(authz_request):
    application_name = "test_app"
    authorized = True
    masked_traits = {"trait1": "value1"}
    paig_policy_ids = [101, 102]
    reason = "Authorization successful"

    response = create_authorize_response(authz_request, application_name, authorized, masked_traits, paig_policy_ids,
                                         reason)

    assert isinstance(response, AuthzResponse)
    assert response.authorized == authorized
    assert response.enforce is True
    assert response.request_id == authz_request.request_id
    assert response.request_date_time == authz_request.request_date_time
    assert response.user_id == authz_request.user_id
    assert response.application_name == application_name
    assert response.masked_traits == masked_traits
    assert response.context == authz_request.context
    assert response.status_code == 200
    assert response.status_message == "Access is allowed"
    assert response.reason == reason
    assert response.paig_policy_ids == paig_policy_ids


def test_create_authorize_response_unauthorized(authz_request):
    application_name = "test_app"
    authorized = False
    masked_traits = {"trait1": "value1"}
    paig_policy_ids = [101, 102]
    reason = "Authorization failed"

    response = create_authorize_response(authz_request, application_name, authorized, masked_traits, paig_policy_ids,
                                         reason)

    assert isinstance(response, AuthzResponse)
    assert response.authorized == authorized
    assert response.enforce is True
    assert response.request_id == authz_request.request_id
    assert response.request_date_time == authz_request.request_date_time
    assert response.user_id == authz_request.user_id
    assert response.application_name == application_name
    assert response.masked_traits == masked_traits
    assert response.context == authz_request.context
    assert response.status_code == 403
    assert response.status_message == "Access is denied"
    assert response.reason == reason
    assert response.paig_policy_ids == paig_policy_ids


def test_create_authorize_vector_db_response(vector_db_authz_request, vector_db_view, vector_db_policy_view):
    policies = [vector_db_policy_view]
    filter_expression = "filter_expression"
    reason = "Authorization successful"

    response = create_authorize_vector_db_response(vector_db_authz_request, vector_db_view, policies, filter_expression,
                                                   reason)

    assert isinstance(response, VectorDBAuthzResponse)
    assert response.vector_db_policy_info == [{"id": vector_db_policy_view.id, "version": ""}]
    assert response.vector_db_id == vector_db_view.id
    assert response.vector_db_name == vector_db_view.name
    assert response.vector_db_type == vector_db_view.type
    assert response.user_enforcement == vector_db_view.user_enforcement
    assert response.group_enforcement == vector_db_view.group_enforcement
    assert response.filter_expression == filter_expression
    assert response.reason == reason


def test_create_authorize_vector_db_response_no_policies(vector_db_authz_request, vector_db_view):
    policies = []
    filter_expression = "filter_expression"
    reason = "Authorization successful"

    response = create_authorize_vector_db_response(vector_db_authz_request, vector_db_view, policies, filter_expression,
                                                   reason)

    assert isinstance(response, VectorDBAuthzResponse)
    assert response.vector_db_policy_info == []
    assert response.vector_db_id == vector_db_view.id
    assert response.vector_db_name == vector_db_view.name
    assert response.vector_db_type == vector_db_view.type
    assert response.user_enforcement == vector_db_view.user_enforcement
    assert response.group_enforcement == vector_db_view.group_enforcement
    assert response.filter_expression == filter_expression
    assert response.reason == reason


def test_create_authorize_vector_db_response_no_vector_db(vector_db_authz_request, vector_db_policy_view):
    policies = [vector_db_policy_view]
    filter_expression = "filter_expression"
    reason = "Authorization successful"

    response = create_authorize_vector_db_response(vector_db_authz_request, None, policies, filter_expression, reason)

    assert isinstance(response, VectorDBAuthzResponse)
    assert response.vector_db_policy_info == [{"id": vector_db_policy_view.id, "version": ""}]
    assert response.vector_db_id is None
    assert response.vector_db_name is None
    assert response.vector_db_type is None
    assert response.user_enforcement is None
    assert response.group_enforcement is None
    assert response.filter_expression == filter_expression
    assert response.reason == reason
