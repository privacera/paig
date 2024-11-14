import pytest
from unittest.mock import MagicMock, AsyncMock

from api.shield.model.shield_audit import ShieldAudit


@pytest.mark.asyncio
async def test_log_message_in_data_service():
    # Arrange
    mock_data_store_controller = MagicMock()
    mock_data_service = MagicMock()
    mock_data_store_controller.get_service.return_value = mock_data_service
    mock_data_service.create_access_audit = AsyncMock()

    log_data = {
        "applicationKey": "test_app_key",
        "applicationName": "test_app_name",
        "clientApplicationKey": "test_client_app_key",
        "clientApplicationName": "test_client_app_name",
        "clientHostname": "test_client_hostname",
        "clientIp": "test_client_ip",
        "context": {"test_context": "test_context"},
        "eventId": "test_event_id",
        "maskedTraits": {"test_masked_traits": "test_masked_traits"},
        "messages": [{"test_messages": "test_messages"}],
        "numberOfTokens": 1,
        "paigPolicyIds": [1],
        "requestId": "test_request_id",
        "requestType": "test_request_type",
        "result": "test_result",
        "tenantId": "test_tenant_id",
        "threadId": "test_thread_id",
        "threadSequenceNumber": 1,
        "traits": ["test_traits"],
        "userId": "test_user_id",
        "encryptionKeyId": 1,
        "eventTime": 1111111111
    }
    log_data = ShieldAudit.from_payload_dict(log_data)
    from api.shield.logfile.log_message_in_data_service import LogMessageInDataService
    service = LogMessageInDataService(mock_data_store_controller)

    # Act
    await service.log(log_data)

    # Assert
    mock_data_service.create_access_audit.assert_awaited_once()
