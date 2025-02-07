import os
import pytest
import json
from unittest.mock import patch
from paig_evaluation.promptfoo_utils import (
    get_suggested_plugins_with_description,
    get_all_security_plugins_with_description,
    read_and_get_security_plugins,
    get_response_object
)


@pytest.fixture
def sample_plugin_file(tmp_path):
    plugin_data = {
        "local_plugins": {
            "plugin_a": "Description for plugin A",
            "plugin_b": "Description for plugin B"
        },
        "remote_plugins": {
            "plugin_c": "Description for plugin C"
        }
    }
    plugin_file = tmp_path / "security_plugins.json"
    with open(plugin_file, "w") as f:
        json.dump(plugin_data, f)
    return plugin_file


def test_get_suggested_plugins_with_description(sample_plugin_file):
    plugins = ["plugin_a", "plugin_d", "plugin_b"]
    with patch("paig_evaluation.promptfoo_utils.read_and_get_security_plugins") as mock_read:
        mock_read.return_value = {
            "plugin_a": "Description for plugin A",
            "plugin_b": "Description for plugin B"
        }
        result = get_suggested_plugins_with_description(plugins)

    expected_result = [
        {"Name": "plugin_a", "Description": "Description for plugin A"},
        {"Name": "plugin_b", "Description": "Description for plugin B"}
    ]
    assert result == expected_result


def test_get_all_security_plugins_with_description(sample_plugin_file):
    result = get_all_security_plugins_with_description(str(sample_plugin_file))

    expected_result = [
        {"Name": "plugin_a", "Description": "Description for plugin A"},
        {"Name": "plugin_b", "Description": "Description for plugin B"},
        {"Name": "plugin_c", "Description": "Description for plugin C"}
    ]
    assert result == expected_result


def test_get_all_security_plugins_with_description_no_file_path():
    result = get_all_security_plugins_with_description("non_existent_file.json")
    assert result == "Error: Security plugins file not found, file_path=non_existent_file.json"


def test_read_and_get_security_plugins_file_not_found():
    result = read_and_get_security_plugins("non_existent_file.json")
    assert result == "Error: Security plugins file not found, file_path=non_existent_file.json"


def test_read_and_get_security_plugins_with_remote_disabled(sample_plugin_file):
    with patch.dict(os.environ, {"PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION": "true"}):
        result = read_and_get_security_plugins(str(sample_plugin_file))

    expected_result = {
        "plugin_a": "Description for plugin A",
        "plugin_b": "Description for plugin B"
    }
    assert result == expected_result


def test_read_and_get_security_plugins_with_remote_enabled(sample_plugin_file):
    with patch.dict(os.environ, {"PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION": "false"}):
        result = read_and_get_security_plugins(str(sample_plugin_file))

    expected_result = {
        "plugin_a": "Description for plugin A",
        "plugin_b": "Description for plugin B",
        "plugin_c": "Description for plugin C"
    }
    assert result == expected_result


def test_read_and_get_security_plugins_with_no_file_path():
    result = read_and_get_security_plugins(None)
    assert result is not None
    assert type(result) == dict


def test_read_and_get_security_plugins_with_invalid_json(sample_plugin_file):
    with patch("paig_evaluation.promptfoo_utils.read_json_file") as mock_load:
        mock_load.return_value = "Invalid JSON data"
        result = read_and_get_security_plugins(sample_plugin_file)
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
