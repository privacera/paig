import pytest
from unittest.mock import patch, MagicMock
from paig_common.async_http_transport import AsyncHttpTransport

@pytest.mark.asyncio
@patch('paig_common.async_http_transport.AsyncHttpTransport.create_default_client')
async def test_setup(mock_create_default_client):
    await AsyncHttpTransport.setup(connect_timeout_sec=5.0, read_timeout_sec=10.0)
    assert AsyncHttpTransport._connect_timeout_sec == 5.0
    assert AsyncHttpTransport._read_timeout_sec == 10.0
    mock_create_default_client.assert_called_once()

@pytest.mark.asyncio
@patch('paig_common.async_http_transport.AsyncHttpTransport.create_default_client')
async def test_get_client(mock_create_default_client):
    AsyncHttpTransport._client = None
    await AsyncHttpTransport.get_client()
    mock_create_default_client.assert_called_once()

@pytest.mark.asyncio
@patch('httpx.AsyncClient')
@patch('httpx.AsyncHTTPTransport')
async def test_create_default_client(mock_async_http_transport, mock_async_client):
    mock_async_http_transport_instance = MagicMock()
    mock_async_http_transport.return_value = mock_async_http_transport_instance
    await AsyncHttpTransport.create_default_client()
    mock_async_client.assert_called_once()