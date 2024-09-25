import pytest
from unittest.mock import AsyncMock
from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from api.authz.services.paig_authorizer_service import PAIGAuthorizerService
from api.authz.controllers.paig_authorizer_controller import PAIGAuthorizerController
from datetime import datetime


@pytest.fixture
def mock_paig_authorizer_service():
    return AsyncMock(spec=PAIGAuthorizerService)


@pytest.fixture
def paig_authorizer_controller(mock_paig_authorizer_service):
    return PAIGAuthorizerController(paig_authorizer_service=mock_paig_authorizer_service)


@pytest.mark.asyncio
async def test_authorize(paig_authorizer_controller, mock_paig_authorizer_service):
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

    mock_paig_authorizer_service.authorize.return_value = AuthzResponse(
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

    response = await paig_authorizer_controller.authorize(request)

    mock_paig_authorizer_service.authorize.assert_awaited_once_with(request)
    assert response.authorized is True


@pytest.mark.asyncio
async def test_authorize_vector_db(paig_authorizer_controller, mock_paig_authorizer_service):
    request = VectorDBAuthzRequest(
        userId="user123",
        applicationKey="app123"
    )

    mock_paig_authorizer_service.authorize_vector_db.return_value = VectorDBAuthzResponse(
        vectorDBPolicyInfo=[{"key1": "value1"}],
        vectorDBId=1,
        vectorDBName="vectorDBName",
        vectorDBType="vectorDBType",
        userEnforcement=0,
        groupEnforcement=1,
        filterExpression="filter_expression",
        reason="None"
    )

    response = await paig_authorizer_controller.authorize_vector_db(request)

    mock_paig_authorizer_service.authorize_vector_db.assert_awaited_once_with(request)
    assert response.vector_db_id == 1
    assert response.vector_db_policy_info == [{"key1": "value1"}]
    assert response.vector_db_name == "vectorDBName"
    assert response.vector_db_type == "vectorDBType"
    assert response.user_enforcement == 0
    assert response.group_enforcement == 1
    assert response.filter_expression == "filter_expression"
    assert response.reason == "None"
