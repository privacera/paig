import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import AsyncMock

from paig_authorizer_core.models.request_models import AuthzRequest, VectorDBAuthzRequest
from paig_authorizer_core.models.response_models import AuthzResponse, VectorDBAuthzResponse
from api.authz.controllers.paig_authorizer_controller import PAIGAuthorizerController


authz_expected_response = AuthzResponse(
        authorized=True,
        enforce=True,
        requestId="req123",
        requestDateTime="2023-07-10T12:34:56.789Z",
        userId="user123",
        applicationName="appName",
        statusCode=0,
        statusMessage="Success",
        reason="None",
        paigPolicyIds=[1, 2, 3]
    )

vector_db_expected_response = VectorDBAuthzResponse(
        vectorDBPolicyInfo=[{"key1": "value1"}],
        vectorDBId=1,
        vectorDBName="vectorDBName",
        vectorDBType="vectorDBType",
        userEnforcement=0,
        groupEnforcement=1,
        filterExpression="filter_expression",
        reason="None"
    )


@pytest.fixture
def mock_paig_authorizer_controller():
    mock_paig_authorizer_controller = AsyncMock(spec=PAIGAuthorizerController)

    mock_paig_authorizer_controller.authorize.return_value = authz_expected_response

    mock_paig_authorizer_controller.authorize_vector_db.return_value = vector_db_expected_response

    return mock_paig_authorizer_controller


@pytest.mark.skip(reason="Need to fix the test by checking how to place mocks here")
@pytest.mark.asyncio
async def test_authorize_route(mock_paig_authorizer_controller, monkeypatch):
    authz_request = AuthzRequest(
        requestId="req123",
        threadId="thread123",
        sequenceNumber=1,
        applicationKey="app123",
        clientApplicationKey="client123",
        userId="user123",
        requestType="prompt",
        traits=["trait1"],
        requestDateTime="2023-07-10T12:34:56.789Z"
    )

    def get_mock_paig_authorizer_controller():
        return mock_paig_authorizer_controller

    monkeypatch.setattr("authz.controllers.paig_authorizer_controller.PAIGAuthorizerController",
                        get_mock_paig_authorizer_controller)

    # Add the router to the FastAPI app
    from api.authz.routes.paig_authorizer_router import paig_authorizer_router
    from server import app

    # Create client
    app.include_router(paig_authorizer_router, prefix="/authz")
    client = TestClient(app)

    authz_request.request_date_time = "2023-07-10T12:34:56.789Z"
    response = client.post("http://localhost:9090/authz",
                           json=authz_request.dict(by_alias=True))

    assert response.status_code == status.HTTP_200_OK
    expected_response_dict = authz_expected_response.dict(by_alias=True)
    expected_response_dict["requestDateTime"] = "2023-07-10T12:34:56.789000Z"
    assert response.json() == expected_response_dict


@pytest.mark.skip(reason="Need to fix the test by checking how to place mocks here")
@pytest.mark.asyncio
async def test_authorize_vector_db_route(mock_paig_authorizer_controller, monkeypatch):
    vector_db_request = VectorDBAuthzRequest(
        userId="user123",
        applicationKey="app123"
    )

    def get_mock_paig_authorizer_controller():
        return mock_paig_authorizer_controller

    monkeypatch.setattr("authz.controllers.paig_authorizer_controller.PAIGAuthorizerController",
                        get_mock_paig_authorizer_controller)

    # Add the router to the FastAPI app
    from api.authz.routes.paig_authorizer_router import paig_authorizer_router
    from server import app

    # Create client
    app.include_router(paig_authorizer_router, prefix="/authz")
    client = TestClient(app)

    response = client.post("http://localhost:9090/authz/vectordb",
                           json=vector_db_request.dict(by_alias=True))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == vector_db_expected_response.dict(by_alias=True)
