import pytest
from unittest.mock import mock_open, patch
import json
import yaml
from paig_evaluation.file_utils import read_json_file, write_json_file, read_yaml_file, write_yaml_file

def test_read_json_file():
    file_path = "test.json"
    mock_data = {"key": "value"}

    # Mock open and json.load
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))) as mock_file, \
         patch("json.load", return_value=mock_data) as mock_json_load:

        result = read_json_file(file_path)

        # Assert that the file was opened in read mode with utf-8 encoding
        mock_file.assert_called_once_with(file_path, "r", encoding="utf-8")
        mock_json_load.assert_called_once()
        assert result == mock_data

def test_write_json_file():
    file_path = "test.json"
    data = {"key": "value"}

    # Mock open and json.dump
    with patch("builtins.open", mock_open()) as mock_file, \
         patch("json.dump") as mock_json_dump:

        write_json_file(file_path, data)

        # Assert that the file was opened in write mode with utf-8 encoding
        mock_file.assert_called_once_with(file_path, "w", encoding="utf-8")
        mock_json_dump.assert_called_once_with(data, mock_file(), indent=4)

def test_read_yaml_file():
    file_path = "test.yaml"
    mock_data = {"key": "value"}

    # Mock open and yaml.safe_load
    with patch("builtins.open", mock_open(read_data=yaml.dump(mock_data))) as mock_file, \
         patch("yaml.safe_load", return_value=mock_data) as mock_yaml_load:

        result = read_yaml_file(file_path)

        # Assert that the file was opened in read mode with utf-8 encoding
        mock_file.assert_called_once_with(file_path, "r", encoding="utf-8")
        mock_yaml_load.assert_called_once()
        assert result == mock_data

def test_write_yaml_file():
    file_path = "test.yaml"
    data = {"key": "value"}

    # Mock open and yaml.safe_dump
    with patch("builtins.open", mock_open()) as mock_file, \
         patch("yaml.safe_dump") as mock_yaml_dump:

        write_yaml_file(file_path, data)

        # Assert that the file was opened in write mode with utf-8 encoding
        mock_file.assert_called_once_with(file_path, "w", encoding="utf-8")
        mock_yaml_dump.assert_called_once_with(data, mock_file(), default_flow_style=False, sort_keys=False)
