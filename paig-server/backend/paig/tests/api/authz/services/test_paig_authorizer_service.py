from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from paig_authorizer_core.async_paig_authorizer import AsyncPAIGAuthorizer
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from api.authz.services.paig_authorizer_service import AuthorizeRequestValidator, PAIGAuthorizerService


# Mock utility functions
@pytest.fixture(autouse=True)
def mock_utils(monkeypatch):
    mock_validate_string_data = Mock()
    mock_validate_id = Mock()
    mock_validate_required_data = Mock()

    monkeypatch.setattr("core.utils.validate_string_data", mock_validate_string_data)
    monkeypatch.setattr("core.utils.validate_id", mock_validate_id)
    monkeypatch.setattr("core.utils.validate_required_data", mock_validate_required_data)

    return mock_validate_string_data, mock_validate_id, mock_validate_required_data


@pytest.fixture
def mock_paig_authorizer():
    return AsyncMock(spec=AsyncPAIGAuthorizer)


@pytest.fixture
def mock_validator():
    return AsyncMock(spec=AuthorizeRequestValidator)


@pytest.mark.asyncio
async def test_validate_authorize_request(mock_utils):
    mock_validate_string_data, mock_validate_id, mock_validate_required_data = mock_utils

    validator = AuthorizeRequestValidator()

    request = AuthzRequest(
        requestId="req123",
        threadId="thread123",
        sequenceNumber=1,
        applicationKey="app123",
        clientApplicationKey="client123",
        userId="user123",
        requestType="prompt",
        traits=["trait1"],
        requestDateTime=datetime.utcnow()
    )

    await validator.validate_authorize_request(request)

    mock_validate_string_data.assert_any_call("req123", "Request ID")
    mock_validate_string_data.assert_any_call("thread123", "Thread ID")
    mock_validate_id.assert_any_call(1, "Sequence Number")
    mock_validate_string_data.assert_any_call("app123", "Application Key")
    mock_validate_string_data.assert_any_call("client123", "Client Application Key")
    mock_validate_string_data.assert_any_call("user123", "User ID")
    mock_validate_string_data.assert_any_call("prompt", "Request Type")
    mock_validate_required_data.assert_any_call(request.request_date_time, "Request Date Time")


@pytest.mark.asyncio
async def test_validate_vector_db_authorize_request(mock_utils):
    mock_validate_string_data, _, _ = mock_utils

    validator = AuthorizeRequestValidator()

    request = VectorDBAuthzRequest(
        userId="user123",
        applicationKey="app123"
    )

    await validator.validate_vector_db_authorize_request(request)

    mock_validate_string_data.assert_any_call("user123", "User ID")
    mock_validate_string_data.assert_any_call("app123", "Application Key")


@pytest.mark.asyncio
async def test_authorize(mock_paig_authorizer, mock_validator):
    service = PAIGAuthorizerService(
        paig_authorizer=mock_paig_authorizer,
        authorize_request_validator=mock_validator
    )

    request = AuthzRequest(
        requestId="req123",
        threadId="thread123",
        sequenceNumber=1,
        applicationKey="app123",
        clientApplicationKey="client123",
        userId="user123",
        requestType="prompt",
        traits=["trait1"],
        requestDateTime=datetime.utcnow()
    )

    mock_paig_authorizer.authorize.return_value = AuthzResponse(
        authorized=True,
        enforce=True,
        requestId="req123",
        requestDateTime=datetime.utcnow(),
        userId="user123",
        applicationName="appName",
        statusCode=0,
        statusMessage="Success",
        reason="None",
        paigPolicyIds=[1, 2, 3]
    )

    response = await service.authorize(request)

    mock_validator.validate_authorize_request.assert_awaited_once_with(request)
    mock_paig_authorizer.authorize.assert_awaited_once_with(request)
    assert response.authorized is True


@pytest.mark.asyncio
async def test_authorize_vector_db(mock_paig_authorizer, mock_validator):
    service = PAIGAuthorizerService(
        paig_authorizer=mock_paig_authorizer,
        authorize_request_validator=mock_validator
    )

    request = VectorDBAuthzRequest(
        userId="user123",
        applicationKey="app123"
    )

    mock_paig_authorizer.authorize_vector_db.return_value = VectorDBAuthzResponse(
        vectorDBPolicyInfo=[{"key1": "value1"}],
        vectorDBId=1,
        vectorDBName="vectorDBName",
        vectorDBType="vectorDBType",
        userEnforcement=0,
        groupEnforcement=1,
        filterExpression="filter_expression",
        reason="None"
    )

    response = await service.authorize_vector_db(request)

    mock_validator.validate_vector_db_authorize_request.assert_awaited_once_with(request)
    mock_paig_authorizer.authorize_vector_db.assert_awaited_once_with(request)
    assert response.vector_db_id == 1
