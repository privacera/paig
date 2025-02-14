import json
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock
from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.authz_service_request import AuthzServiceRequest
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.vectordb_authz_response import AuthorizeVectorDBResponse


def authorize_req_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authorize_request.json"
    with open(json_file_path, 'r') as json_file:
        req_json = json.load(json_file)

    return AuthorizeRequest(tenant_id='test_tenant', req_data=req_json, user_role='OWNER')


def get_authz_service_request():
    auth_req = authorize_req_data()
    return AuthzServiceRequest(
        auth_req=auth_req,
        traits=['trait1', 'trait2']
    )


def create_mock_authz_response(mock_authz_response):
    mock_authz_response.reason = 'reason'
    mock_authz_response.authorized = True
    mock_authz_response.enforce = True
    mock_authz_response.request_id = '55ee-91c2-9e05a1ebe151'
    mock_authz_response.application_name = 'saitama'
    mock_authz_response.masked_traits = {"PERSON": "<<PERSON>>",
                                         "LOCATION": "<<LOCATION>>"}
    mock_authz_response.context = "context",
    mock_authz_response.paig_policy_ids = ["paig_policy_id1", "paig_policy_id2"]
    mock_authz_response.status_code = 0
    mock_authz_response.status_message = "Access is allowed"
    mock_authz_response.user_id = "user_id"


def create_mock_vectordb_response(mock_vectordb_response):
    mock_vectordb_response.vector_db_policy_info = [{"policy1": "policy1"}, {"policy2": "policy2"}]
    mock_vectordb_response.vector_db_id = 1
    mock_vectordb_response.vector_db_name = "vectordb_name"
    mock_vectordb_response.vector_db_type = "vectordb_type"
    mock_vectordb_response.user_enforcement = 1
    mock_vectordb_response.group_enforcement = 1
    mock_vectordb_response.filter_expression = "filter_expression"
    mock_vectordb_response.reason = ""


class TestLocalAuthzClient:
    @pytest.fixture
    def mock_paig_authorizer(self):
        from paig_authorizer_core.async_paig_authorizer import AsyncPAIGAuthorizer
        return MagicMock(spec=AsyncPAIGAuthorizer)

    @pytest.fixture
    def client(self, mock_paig_authorizer):
        from api.shield.client.local_authz_service_client import LocalAuthzClient
        return LocalAuthzClient(mock_paig_authorizer)

    @pytest.mark.asyncio
    async def test_post_authorize(self, client, mock_paig_authorizer):
        # Arrange
        tenant_id = "test_tenant"
        mock_authz_service_request = get_authz_service_request()
        from paig_authorizer_core.models.response_models import AuthzResponse
        mock_authz_response = MagicMock(spec=AuthzResponse)
        create_mock_authz_response(mock_authz_response)
        mock_paig_authorizer.authorize = AsyncMock(return_value=mock_authz_response)

        # Act
        result = await client.post_authorize(mock_authz_service_request, tenant_id)

        # Assert
        mock_paig_authorizer.authorize.assert_awaited_once()
        assert isinstance(result, AuthzServiceResponse)

    @pytest.mark.asyncio
    async def test_post_authorize_vectordb(self, client, mock_paig_authorizer):
        # Arrange
        tenant_id = "test_tenant"
        mock_vectordb_auth_req = AuthorizeVectorDBRequest({"userId": "userId", "applicationKey": "applicationKey",
                                                           }, user_role=None)
        from paig_authorizer_core.models.response_models import VectorDBAuthzResponse
        mock_vectordb_response = MagicMock(spec=VectorDBAuthzResponse)
        create_mock_vectordb_response(mock_vectordb_response)
        mock_paig_authorizer.authorize_vector_db = AsyncMock(return_value=mock_vectordb_response)

        # Act
        result = await client.post_authorize_vectordb(mock_vectordb_auth_req, tenant_id)

        # Assert
        mock_paig_authorizer.authorize_vector_db.assert_awaited_once()
        assert isinstance(result, AuthorizeVectorDBResponse)
