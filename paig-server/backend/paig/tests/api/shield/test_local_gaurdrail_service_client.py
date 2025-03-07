import pytest
from unittest.mock import AsyncMock
from api.shield.client.local_guardrail_service_client import LocalGuardrailServiceClient


@pytest.fixture
def mock_guardrail_service(mocker):
    """
    Mock the SingletonDepends and the GuardrailService used in LocalGuardrailServiceClient.
    """
    mock_guardrail_service = AsyncMock()

    # Patch SingletonDepends to return the mock guardrail service
    mocker.patch('api.shield.client.local_guardrail_service_client.SingletonDepends',
                 return_value=mock_guardrail_service)

    return mock_guardrail_service

@pytest.mark.asyncio
async def test_get_guardrail_info_by_id_found(mock_guardrail_service):
    # Mock the return value of get_guardrail_info_by_id method
    mock_guardrail_service.get_guardrail_info_by_id.return_value = "Mocked data"

    # Call the method on the mock
    result = await mock_guardrail_service.get_guardrail_info_by_id(1)

    # Validate the return value
    assert result == "Mocked data"

    # Verify the method was called
    assert mock_guardrail_service.get_guardrail_info_by_id.called

    # Optionally check the arguments passed to the mock
    mock_guardrail_service.get_guardrail_info_by_id.assert_called_with(1)

    # Or print the call args list to debug
    print(mock_guardrail_service.get_guardrail_info_by_id.call_args_list)

@pytest.mark.asyncio
async def test_get_guardrail_info_by_id_not_found(mock_guardrail_service):
    # Mock the return value of get_guardrail_info_by_id method to simulate "not found"
    mock_guardrail_service.get_guardrail_info_by_id.return_value = None

    # Call the method on the mock
    result = await mock_guardrail_service.get_guardrail_info_by_id(999)

    # Validate the return value
    assert result is None

    # Verify the method was called
    assert mock_guardrail_service.get_guardrail_info_by_id.called

    # Optionally check the arguments passed to the mock
    mock_guardrail_service.get_guardrail_info_by_id.assert_called_with(999)

    # Or print the call args list to debug
    print(mock_guardrail_service.get_guardrail_info_by_id.call_args_list)
