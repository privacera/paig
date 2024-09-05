import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from paig_common.async_base_rest_http_client import AsyncBaseRESTHttpClient, AsyncReturnValue


@pytest.mark.asyncio
@patch('paig_common.async_http_transport.AsyncHttpTransport.setup')
@patch('paig_common.config_utils.get_property_value_int')
@patch('paig_common.config_utils.get_property_value')
@patch('paig_common.config_utils.get_property_value_float')
async def test_setup(mock_get_property_value_float, mock_get_property_value, mock_get_property_value_int, mock_setup):
    mock_get_property_value_int.side_effect = [4, 1]
    mock_get_property_value.side_effect = ['["GET", "POST", "PUT", "DELETE"]', '[500, 502, 503, 504]']
    mock_get_property_value_float.side_effect = [2.0, 7.0]

    client = AsyncBaseRESTHttpClient("http://example.com")
    await client.setup()

    mock_setup.assert_called_once_with(
        connect_timeout_sec=2.0,
        read_timeout_sec=7.0
    )


def test_get_auth():
    client = AsyncBaseRESTHttpClient("http://example.com")
    assert client.get_auth() is None


def test_get_default_headers():
    client = AsyncBaseRESTHttpClient("http://example.com")
    headers = client.get_default_headers()
    assert headers == {"Content-Type": "application/json", "Accept": "application/json"}


@pytest.mark.asyncio
@patch('paig_common.async_http_transport.AsyncHttpTransport.get_client')
@patch('httpx.Response')
async def test_request(mock_response, mock_get_client):
    mock_client = AsyncMock()
    mock_get_client.return_value = mock_client
    mock_response.status_code = 200
    mock_response.text = '{"key": "value"}'
    mock_client.request.return_value = mock_response

    client = AsyncBaseRESTHttpClient("http://example.com")
    response = await client.request(url="/test", method="GET")

    assert isinstance(response, AsyncReturnValue)
    assert response.status_code == 200
    assert response.json() == {"key": "value"}


@pytest.mark.asyncio
@patch('paig_common.async_base_rest_http_client.AsyncBaseRESTHttpClient.request')
async def test_http_methods(mock_request):
    client = AsyncBaseRESTHttpClient("http://example.com")

    await client.get(url="/test")
    mock_request.assert_called_with(method='GET', url="/test")

    await client.post(url="/test")
    mock_request.assert_called_with(method='POST', url="/test")

    await client.put(url="/test")
    mock_request.assert_called_with(method='PUT', url="/test")

    await client.delete(url="/test")
    mock_request.assert_called_with(method='DELETE', url="/test")

    await client.patch(url="/test")
    mock_request.assert_called_with(method='PATCH', url="/test")
