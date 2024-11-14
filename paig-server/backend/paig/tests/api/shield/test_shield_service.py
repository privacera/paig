import json
from pathlib import Path

import pytest
from unittest.mock import MagicMock, AsyncMock

from api.shield.model.vectordb_authz_response import AuthorizeVectorDBResponse
from api.shield.model.authorize_request import AuthorizeRequest


def authorize_req_data():
    json_file_path = f"{Path(__file__).parent}/json_data/authorize_request.json"
    with open(json_file_path, 'r') as json_file:
        req_json = json.load(json_file)

    return AuthorizeRequest(tenant_id='test_tenant', req_data=req_json, user_role='OWNER')


@pytest.mark.asyncio
async def test_initialize_tenant():
    from api.shield.services.shield_service import ShieldService
    # Arrange
    mock_auth_service = MagicMock()
    mock_auth_service.tenant_data_encryptor_service.get_data_encryptor = AsyncMock()
    mock_auth_service.application_manager.load_scanners = MagicMock()
    service = ShieldService(mock_auth_service)

    # Act
    await service.initialize_tenant("test_tenant_id", "test_user_role", "test_server_key_id", "test_plugin_key_id",
                                    "test_application_key")

    # Assert
    mock_auth_service.tenant_data_encryptor_service.get_data_encryptor.assert_awaited()
    mock_auth_service.application_manager.load_scanners.assert_called_once_with(application_key="test_application_key")


@pytest.mark.asyncio
async def test_authorize():
    # Arrange
    from api.shield.services.shield_service import ShieldService
    mock_auth_service = MagicMock()
    mock_auth_service.authorize = AsyncMock()
    service = ShieldService(mock_auth_service)
    auth_req = authorize_req_data()

    # Act
    await service.authorize(auth_req)

    # Assert
    mock_auth_service.authorize.assert_awaited_once_with(auth_req)


@pytest.mark.asyncio
async def test_authorize_vectordb():
    # Arrange
    mock_auth_service = MagicMock()
    mock_vectordb_response = MagicMock(spec=AuthorizeVectorDBResponse)
    mock_vectordb_response.__dict__ = {"key": "value"}
    mock_auth_service.authorize_vectordb = AsyncMock(return_value=mock_vectordb_response)
    from api.shield.services.shield_service import ShieldService
    service = ShieldService(mock_auth_service)

    # Act
    await service.authorize_vectordb("test_tenant_id", "test_user_role",
                                     {"userId": "test_user_id", "applicationKey": "test_application_key"})

    # Assert
    mock_auth_service.authorize_vectordb.assert_awaited()


@pytest.mark.asyncio
async def test_audit():
    # Arrange
    mock_auth_service = MagicMock()
    mock_auth_service.audit_stream_data = AsyncMock()
    from api.shield.services.shield_service import ShieldService
    service = ShieldService(mock_auth_service)
    request = {
        "applicationKey": "test_app_key",
        "applicationName": "test_app_name",
        "clientApplicationKey": "test_client_app_key",
        "clientApplicationName": "test_client_app_name",
        "clientHostname": "test_client_hostname",
        "clientIp": "test_client_ip",
        "context": "test_context",
        "eventId": "test_event_id",
        "maskedTraits": "test_masked_traits",
        "messages": "test_messages",
        "numberOfTokens": 1,
        "paigPolicyIds": "test_paig_policy_ids",
        "requestId": "test_request_id",
        "requestType": "test_request_type",
        "result": "test_result",
        "tenantId": "test_tenant_id",
        "threadId": "test_thread_id",
        "threadSequenceNumber": 1,
        "traits": "test_traits",
        "userId": "test_user_id",
        "encryptionKeyId": "test_encryption_key_id",
        "eventTime": "test_event_time"
    }

    # Act
    await service.audit(request)

    # Assert
    mock_auth_service.audit_stream_data.assert_awaited_once()