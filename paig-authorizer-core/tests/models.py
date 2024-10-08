import pytest
from pydantic import ValidationError
from datetime import datetime

from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse


def test_authz_request_valid():
    request = AuthzRequest(
        conversationId="conv123",
        requestId="req123",
        threadId="thread123",
        sequenceNumber=1,
        applicationKey="app123",
        clientApplicationKey="client123",
        enforce=True,
        userId="user123",
        requestType="prompt",
        traits=["trait1", "trait2"],
        context={"key1": "value1"},
        requestDateTime=datetime.now()
    )
    assert request.conversation_id == "conv123"
    assert request.request_id == "req123"
    assert request.thread_id == "thread123"
    assert request.sequence_number == 1
    assert request.application_key == "app123"
    assert request.client_application_key == "client123"
    assert request.enforce is True
    assert request.user_id == "user123"
    assert request.request_type == "prompt"
    assert request.traits == ["trait1", "trait2"]
    assert request.context == {"key1": "value1"}


def test_authz_request_defaults():
    request = AuthzRequest(
        requestId="req123",
        threadId="thread123",
        applicationKey="app123",
        userId="user123",
        requestType="prompt",
        traits=["trait1", "trait2"]
    )
    assert request.sequence_number == 0
    assert request.client_application_key == "unknown"
    assert request.enforce is True
    assert isinstance(request.request_date_time, datetime)


def test_authz_request_invalid():
    with pytest.raises(ValidationError):
        AuthzRequest(
            requestId="req123",
            threadId="thread123",
            applicationKey="app123",
            userId="user123",
            requestType="prompt",
            traits="trait1"  # Invalid type, should be a list
        )


def test_authz_response_valid():
    response = AuthzResponse(
        authorized=True,
        enforce=True,
        requestId="req123",
        requestDateTime=datetime.now(),
        userId="user123",
        applicationName="appName",
        maskedTraits={"trait1": "masked1"},
        context={"key1": "value1"},
        statusCode=0,
        statusMessage="Success",
        reason="None",
        paigPolicyIds=[1, 2, 3]
    )
    assert response.authorized is True
    assert response.enforce is True
    assert response.request_id == "req123"
    assert isinstance(response.request_date_time, datetime)
    assert response.user_id == "user123"
    assert response.application_name == "appName"
    assert response.masked_traits == {"trait1": "masked1"}
    assert response.context == {"key1": "value1"}
    assert response.status_code == 0
    assert response.status_message == "Success"
    assert response.reason == "None"
    assert response.paig_policy_ids == [1, 2, 3]


def test_authz_response_invalid():
    with pytest.raises(ValidationError):
        AuthzResponse(
            authorized=True,
            enforce=True,
            requestId="req123",
            requestDateTime="invalid_date",  # Invalid datetime format
            userId="user123",
            applicationName="appName",
            maskedTraits={"trait1": "masked1"},
            context={"key1": "value1"},
            statusCode=0,
            statusMessage="Success",
            reason="None",
            paigPolicyIds=[1, 2, 3]
        )


def test_vector_db_authz_request_valid():
    request = VectorDBAuthzRequest(
        userId="user123",
        applicationKey="app123"
    )
    assert request.user_id == "user123"
    assert request.application_key == "app123"


def test_vector_db_authz_request_invalid():
    with pytest.raises(ValidationError):
        VectorDBAuthzRequest(
            userId=None,  # Mandatory field missing
            applicationKey="app123"
        )


def test_vector_db_authz_response_valid():
    response = VectorDBAuthzResponse(
        vectorDBPolicyInfo=[{"key1": "value1"}],
        vectorDBId=1,
        vectorDBName="vectorDBName",
        vectorDBType="vectorDBType",
        userEnforcement=0,
        groupEnforcement=1,
        filterExpression="filter_expression",
        reason="None"
    )
    assert response.vector_db_policy_info == [{"key1": "value1"}]
    assert response.vector_db_id == 1
    assert response.vector_db_name == "vectorDBName"
    assert response.vector_db_type == "vectorDBType"
    assert response.user_enforcement == 0
    assert response.group_enforcement == 1
    assert response.filter_expression == "filter_expression"
    assert response.reason == "None"


def test_vector_db_authz_response_invalid():
    with pytest.raises(ValidationError):
        VectorDBAuthzResponse(
            vectorDBPolicyInfo="invalid",  # Invalid type, should be a list
            vectorDBId=1,
            vectorDBName="vectorDBName",
            vectorDBType="vectorDBType",
            userEnforcement=0,
            groupEnforcement=1,
            filterExpression="filter_expression",
            reason="None"
        )
