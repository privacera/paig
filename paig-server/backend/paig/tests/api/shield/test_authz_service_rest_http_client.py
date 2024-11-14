import json

import pytest

from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.vectordb_authz_request import AuthorizeVectorDBRequest
from api.shield.model.authz_service_request import AuthzServiceRequest
from api.shield.model.authz_service_response import AuthzServiceResponse
from api.shield.utils import config_utils
from api.shield.utils.custom_exceptions import BadRequestException, ShieldException
from requests.models import Response


def get_authz_request_data():
    req_data = {
        "threadId": "12345",
        "requestId": "67890",
        "sequenceNumber": 1,
        "requestType": "example",
        "userId": "example_user_id",
        "requestDateTime": "2022-01-01 12:00:00",
        "applicationKey": "app_key",
        "clientApplicationKey": "client_app_key",
        "shieldServerKeyId": "server_key_id",
        "shieldPluginKeyId": "plugin_key_id"
    }
    tenant_id = "test_tenant"
    user_role = "OWNER"
    authorize_request = AuthorizeRequest(req_data, tenant_id, user_role)
    traits = ["example_trait_1", "example_trait_2"]
    return AuthzServiceRequest(authorize_request, traits)


class TestHttpAuthzClient:

    #  can make a successful POST request to the API with valid AuthzServiceRequest data
    @pytest.mark.asyncio
    async def test_successful_post_request_with_valid_authz_service_request_data(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()

        # Act
        authz_req = get_authz_request_data()
        response_data = (b'{"authorized": true, "enforce": true, "request_id": "example_request_id", "audit_id": '
                         b'"example_audit_id", "application_name": "example_application_name", "masked_traits": {}, '
                         b'"context": {}, "ranger_audit_ids": [], "ranger_policy_ids": [], "paig_policy_ids": [], '
                         b'"status_code": 1, "status_message": "Success", "user_id": "example_user_id"}')

        str_response_data = response_data.decode('utf-8')
        response = Response()
        response.status_code = 200
        response.__dict__['_content'] = response_data

        mocker.patch.object(client, 'post', return_value=response)

        # Act
        result = await client.post_authorize(authz_req, "example_tenant_id")

        # Assert
        assert result.__dict__ == AuthzServiceResponse(json.loads(str_response_data)).__dict__

    #  can make a successful POST request to the API with valid AuthorizeVectorDBRequest data
    @pytest.mark.asyncio
    async def test_successful_post_request_with_valid_authorize_vectordb_request_data(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        req_data = {"userId": "example_user_id", "applicationKey": "example_app_key"}
        tenant_id = "example_tenant_id"
        user_role = "OWNER"

        authz_req = AuthorizeVectorDBRequest(req_data, user_role)

        response_data = b'{"vectorDBPolicyInfo": [],"vectorDBId":"2","vectorDBName":"test-vectordb","vectorDBType":"MILVUS","userEnforcement":"1","groupEnforcement":"1","filterExpression":"(array_contains(users, \'akhilesh.gupta\')) && (((((exists metadata[\'region\']) && (metadata[\'region\'] != \'IND\')) || (not exists metadata[\'region\'])) && (((exists metadata[\'region\']) && (metadata[\'region\'] != \'SA\')) || (not exists metadata[\'region\']))) && ((((exists metadata[\'security\']) && (metadata[\'security\'] == \'confidential\')) || (not exists metadata[\'security\'])) || (((exists metadata[\'security\']) && (metadata[\'security\'] == \'restricted\')) || (not exists metadata[\'security\']))))"}'
        str_response_data = response_data.decode('utf-8')
        response = Response()
        response.status_code = 200
        response.__dict__['_content'] = response_data
        mocker.patch.object(client, 'post', return_value=response)

        # Act
        result = await client.post_authorize_vectordb(authz_req, tenant_id)

        # Assert
        assert result.__dict__ == json.loads(str_response_data)

    #  can handle a POST request to the API with valid AuthorizeVectorDBRequest data but error in response
    @pytest.mark.asyncio
    async def test_post_request_with_error_authorize_vectordb_response(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        req_data = {"userId": "example_user_id", "applicationKey": "example_app_key"}
        tenant_id = "example_tenant_id"
        user_role = "OWNER"

        authz_req = AuthorizeVectorDBRequest(req_data, user_role)

        response = Response()
        response.status_code = 500
        mocker.patch.object(client, 'post', return_value=response)

        # Act
        with pytest.raises(Exception):
            await client.post_authorize_vectordb(authz_req, tenant_id)

        # Assert

    #  can make a successful POST request to the API to initialize authorization
    @pytest.mark.asyncio
    async def test_successful_post_request_to_initialize_authorization(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        tenant_id = "example_tenant_id"
        user_role = "OWNER"

        response = Response()
        response.status_code = 200
        mocker.patch.object(client, 'post', return_value=response)

        side_effect = lambda prop: {
            "authz_init_endpoint": "/authz/init"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Act
        await client.post_init_authz(tenant_id, user_role)

        # Assert
        client.post.assert_called_once_with(url="/authz/init", headers=client.get_headers(tenant_id, user_role), json={})

    @pytest.mark.asyncio
    async def test_successful_post_request_to_initialize_authorization_with_application_key(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        tenant_id = "example_tenant_id"
        user_role = "OWNER"

        response = Response()
        response.status_code = 200
        mocker.patch.object(client, 'post', return_value=response)

        side_effect = lambda prop: {
            "authz_init_endpoint": "/authz/init"
        }.get(prop)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        # Act
        await client.post_init_authz(tenant_id, user_role, application_key="example_app_key")

        # Assert
        client.post.assert_called_once_with(url="/authz/init", headers=client.get_headers(tenant_id, user_role),
                                            json={"applicationKey": "example_app_key"})

    @pytest.mark.asyncio
    async def test_error_on_post_request_to_initialize_authorization(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        tenant_id = "example_tenant_id"
        user_role = "OWNER"

        response = Response()
        response.status_code = 400
        mocker.patch.object(client, 'post', return_value=response)

        # Act
        with pytest.raises(Exception) as e:
            await client.post_init_authz(tenant_id, user_role)

        print(f"\nGot exception=> {e.type}: {e.value}")

    #  can handle missing paig_api_key when getting headers
    def test_handle_missing_paig_api_key_when_getting_headers(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        tenant_id = "example_tenant_id"
        user_role = "OWNER"
        mocker.patch.object(config_utils, 'get_property_value', return_value=None)

        # Act
        headers = client.get_headers(tenant_id, user_role)

        # Assert
        assert headers == {"x-tenant-id": tenant_id, "x-user-role": user_role}

        #  can handle having paig_api_key when getting headers

    def test_having_paig_api_key_when_getting_headers(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        tenant_id = "example_tenant_id"
        user_role = "OWNER"
        api_key = "sample-api-key"

        mocker.patch("api.shield.client.http_authz_service_client.config_utils.get_property_value",
                     return_value=api_key)

        # Act
        headers = client.get_headers(tenant_id, user_role)

        # Assert
        assert headers == {"x-paig-api-key": api_key}

    #  can handle unsuccessful POST request to the API with invalid AuthzServiceRequest data
    @pytest.mark.asyncio
    async def test_handle_unsuccessful_post_request_with_invalid_authz_service_request_data(self, mocker):
        from api.shield.client.http_authz_service_client import HttpAuthzClient
        # Arrange
        client = HttpAuthzClient()
        auth_req = get_authz_request_data()

        res = Response()
        res.status_code = 400
        res.__dict__['_content'] = b'Bad Request'

        mocker.patch.object(client, 'post', return_value=res)

        # Act/Assert
        with pytest.raises(ShieldException):
            await client.post_authorize(auth_req, "example_tenant_id")

    #  can handle missing request data when creating AuthorizeVectorDBRequest objects
    def test_handle_missing_request_data_when_creating_request_objects(self):
        # Arrange
        vectordb_req_data = {"applicationKey": "example_app_key"}
        user_role = "OWNER"

        # Act/Assert
        with pytest.raises(BadRequestException):
            AuthorizeVectorDBRequest(vectordb_req_data, user_role)

    # handle request type being enriched_prompt or rag in the authz request
    def test_set_request_type_to_request_type_field_when_enriched_prompt_or_rag(self):
        # Arrange
        req_data = {
            "threadId": "123",
            "requestId": "456",
            "sequenceNumber": 1,
            "requestType": "enriched_prompt",
            "requestDateTime": "2022-01-01T00:00:00Z",
            "applicationKey": "app_key",
            "clientApplicationKey": "client_app_key",
            "shieldServerKeyId": "server_key_id",
            "shieldPluginKeyId": "plugin_key_id",
            "messages": [],
            "conversationId": "conv_id",
            "userId": "user_id",
            "context": {},
            "clientIp": "127.0.0.1",
            "clientHostName": "localhost"
        }
        traits = ["trait1", "trait2"]

        # Act
        authz_request = AuthzServiceRequest(AuthorizeRequest(req_data, "tenant_id", "OWNER"), traits)

        # Assert
        assert authz_request.requestType == "prompt"
