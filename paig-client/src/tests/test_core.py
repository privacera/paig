import unittest
import base64
import os
import json
from paig_client.core import PAIGApplication
from paig_client.exception import PAIGException
from unittest.mock import patch, MagicMock

@patch("paig_client.core.HttpTransport.get_http")
def test_fetch_application_config_from_server_success(mock_http_transport):
    api_key = base64.urlsafe_b64encode(b"test_api_key;https://paig-server.com").decode("utf-8")
    mock_response = MagicMock()
    mock_response.status = 200
    mock_response.json.return_value = {"key": "value"}
    mock_http_transport.return_value.request.return_value = mock_response
    result = PAIGApplication.fetch_application_config_from_server(api_key, {})
    assert result["key"] == "value"
    assert result["apiServerUrl"] == "https://paig-server.com"
    assert result["apiKey"] == api_key


def test_fetch_application_config_from_server_invalid_api_key_format():
    invalid_api_key = base64.urlsafe_b64encode(b"invalid_key").decode("utf-8")
    with unittest.TestCase().assertRaises(ValueError) as context:
        PAIGApplication.fetch_application_config_from_server(invalid_api_key, {})
    assert "Failed to fetch configuration from the server. Please ensure API key is valid." in str(context.exception)


def test_fetch_application_config_from_server_invalid_url():
    invalid_url_key = base64.urlsafe_b64encode(b"test_api_key;invalid_url").decode("utf-8")
    with unittest.TestCase().assertRaises(ValueError) as context:
        PAIGApplication.fetch_application_config_from_server(invalid_url_key, {})
    assert "Failed to fetch configuration from the server. Please ensure API key is valid." in str(context.exception)


@patch("paig_client.core.HttpTransport.get_http")
def test_fetch_application_config_from_server_http_error(mock_http_transport):
    api_key = base64.urlsafe_b64encode(b"test_api_key;https://paig-server.com").decode("utf-8")
    mock_response = MagicMock()
    mock_response.status = 500
    mock_response.data = "Internal Server Error"
    mock_http_transport.return_value.request.return_value = mock_response
    with unittest.TestCase().assertRaises(ValueError) as context:
        PAIGApplication.fetch_application_config_from_server(api_key, {})
    assert "Failed to fetch configuration from the server. Please ensure API key is valid." in str(context.exception)


@patch("paig_client.core.HttpTransport.get_http")
def test_fetch_application_config_from_server_exception_handling(mock_http_transport):
    api_key = base64.urlsafe_b64encode(b"test_api_key;https://paig-server.com").decode("utf-8")
    mock_http_transport.return_value.request.side_effect = Exception("Network error")
    with unittest.TestCase().assertRaises(ValueError) as context:
        PAIGApplication.fetch_application_config_from_server(api_key, {})
    assert "Failed to fetch configuration from the server. Please ensure API key is valid." in str(context.exception)


def test_fetch_application_config_file_if_apikey_is_not_present(setup_curr_dir):
    result = PAIGApplication.fetch_application_config_from_server(
        None, {"application_config_file": setup_curr_dir + "/data/privacera-shield-test-config.json"}
    )
    assert result["key"] == "value"
    assert result["apiServerUrl"] == "https://paig-server.com"
    assert result["apiKey"] == "apikey"


def test_get_plugin_app_config_with_dict():
    kwargs = {"application_config": {"key": "value"}}
    result = PAIGApplication.get_plugin_app_config(kwargs)
    assert result == {"key": "value"}


def test_get_plugin_app_config_with_valid_json_string():
    kwargs = {"application_config": json.dumps({"key": "value"})}
    result = PAIGApplication.get_plugin_app_config(kwargs)
    assert result == {"key": "value"}


def test_get_plugin_app_config_with_invalid_json_string():
    kwargs = {"application_config": "{invalid_json}"}
    with unittest.TestCase().assertRaises(PAIGException) as context:
        PAIGApplication.get_plugin_app_config(kwargs)
    assert "ERROR: PAIG-400013" in str(context.exception)


def test_get_plugin_app_config_with_invalid_type():
    kwargs = {"application_config": 12345}
    with unittest.TestCase().assertRaises(PAIGException) as context:
        PAIGApplication.get_plugin_app_config(kwargs)
    assert "ERROR: PAIG-400014" in str(context.exception)


@patch.object(PAIGApplication, 'fetch_application_config_from_server')
def test_get_plugin_app_config_with_api_key(mock_fetch_config):
    mock_fetch_config.return_value = {"apiKeyConfig": "valueFromServer"}
    kwargs = {"application_config_api_key": "test-api-key"}
    result = PAIGApplication.get_plugin_app_config(kwargs)
    assert result == {"apiKeyConfig": "valueFromServer"}
    mock_fetch_config.assert_called_with("test-api-key", kwargs)


@patch.object(PAIGApplication, 'fetch_application_config_from_server')
def test_get_plugin_app_config_with_env_api_key(mock_fetch_config):
    mock_fetch_config.return_value = {"apiKeyConfig": "valueFromEnv"}
    with patch.dict(os.environ, {"PAIG_API_KEY": "env-api-key"}):
        result = PAIGApplication.get_plugin_app_config({})
        assert result == {"apiKeyConfig": "valueFromEnv"}
        mock_fetch_config.assert_called_with("env-api-key", {})


@patch.object(PAIGApplication, 'fetch_application_config_from_server')
def test_get_plugin_app_config_without_api_key(mock_fetch_config):
    mock_fetch_config.return_value = {"defaultConfig": "defaultValue"}
    with patch.dict(os.environ, {}, clear=True):
        result = PAIGApplication.get_plugin_app_config({})
        assert result == {"defaultConfig": "defaultValue"}
        mock_fetch_config.assert_called_with(None, {})
