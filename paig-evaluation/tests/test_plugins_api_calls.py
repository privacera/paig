import os
import pytest
import json
from unittest.mock import patch
from paig_evaluation.promptfoo_utils import (
    get_suggested_plugins_with_info,
    get_all_security_plugins_with_info,
    read_and_get_security_plugins,
    get_response_object,
    constants
)


plugin_data = {
        "plugin_a": {
            "description": "Description for plugin A",
            "severity": "CRITICAL",
            "type": "Trust & Safety",
            "remote": False
        },
        "plugin_b": {
            "description": "Description for plugin B",
            "severity": "CRITICAL",
            "type": "Trust & Safety",
            "remote": False
        },
        "plugin_c": {
            "description": "Description for plugin C",
            "severity": "CRITICAL",
            "type": "Trust & Safety",
            "remote": True
        }
}

@pytest.fixture
def sample_plugin_file(tmp_path):
    plugin_file = tmp_path / "security_plugins.json"
    with open(plugin_file, "w") as f:
        json.dump(plugin_data, f)
    return plugin_file


def test_get_suggested_plugins_with_info(sample_plugin_file):
    plugins = ["plugin_a", "plugin_d", "plugin_b"]
    with patch("paig_evaluation.promptfoo_utils.read_and_get_security_plugins") as mock_read:
        mock_read.return_value = plugin_data
        result = get_suggested_plugins_with_info(plugins)

    assert all(any(item['Name'] == plugin['Name'] and item['Description'] == plugin['Description'] for plugin in
                   result) for item in [
                    {"Name": "plugin_a", "Description": "Description for plugin A"},
                    {"Name": "plugin_b", "Description": "Description for plugin B"}
               ])


def test_get_all_security_plugins_with_info(sample_plugin_file):
    with patch("paig_evaluation.promptfoo_utils.read_and_get_security_plugins") as mock_read:
        mock_read.return_value = plugin_data
        result = get_all_security_plugins_with_info()
    assert all(any(item['Name'] == plugin['Name'] and item['Description'] == plugin['Description'] for plugin in
                   result) for item in [
                    {"Name": "plugin_a", "Description": "Description for plugin A"},
                    {"Name": "plugin_b", "Description": "Description for plugin B"},
                    {"Name": "plugin_c", "Description": "Description for plugin C"}
               ])


def test_read_and_get_security_plugins_with_remote_disabled(sample_plugin_file):
    constants.PLUGIN_FILE_PATH = sample_plugin_file
    constants.DEFAULT_PLUGIN_FILE_PATH = sample_plugin_file
    with patch.dict(os.environ, {"PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION": "true"}):
        result = read_and_get_security_plugins()

    expected_result = {
        "plugin_a": "Description for plugin A",
        "plugin_b": "Description for plugin B"
    }
    assert result.keys() == expected_result.keys()


def test_read_and_get_security_plugins_with_remote_enabled(sample_plugin_file):
    with patch.dict(os.environ, {"PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION": "false"}):
        result = read_and_get_security_plugins()

    expected_result = {
        "plugin_a": "Description for plugin A",
        "plugin_b": "Description for plugin B",
        "plugin_c": "Description for plugin C"
    }
    assert result.keys() == expected_result.keys()


def test_read_and_get_security_plugins_with_no_file_path():
    result = read_and_get_security_plugins()
    assert result is not None
    assert type(result) == dict


def test_read_and_get_security_plugins_with_invalid_json(sample_plugin_file):
    with patch("paig_evaluation.promptfoo_utils.read_json_file") as mock_load:
        mock_load.return_value = "Invalid JSON data"
        result = read_and_get_security_plugins()
    assert result is not None
    assert type(result) == str


def test_get_response_object():
    expected_response = {
        "status": "failed",
        "message": "",
        "result": None
    }
    response = get_response_object()
    assert response == expected_response
