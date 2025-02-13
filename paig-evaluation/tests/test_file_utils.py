import pytest
import tempfile
import json
import yaml
from paig_evaluation.file_utils import (
    read_json_file,
    write_json_file,
    read_yaml_file,
    write_yaml_file
)


@pytest.fixture
def sample_json_data():
    return {"name": "John", "age": 30, "active": True}


@pytest.fixture
def sample_yaml_data():
    return {"name": "Alice", "age": 25, "skills": ["Python", "FastAPI"]}


def test_write_and_read_json_file(sample_json_data):
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        file_path = temp_file.name

    # Write JSON file
    write_json_file(file_path, sample_json_data)

    # Read JSON file
    result = read_json_file(file_path)

    # Assertions
    assert result == sample_json_data


def test_write_and_read_yaml_file(sample_yaml_data):
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp_file:
        file_path = temp_file.name

    # Write YAML file
    write_yaml_file(file_path, sample_yaml_data)

    # Read YAML file
    result = read_yaml_file(file_path)

    # Assertions
    assert result == sample_yaml_data


def test_json_file_content_structure(sample_json_data):
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_file:
        file_path = temp_file.name

    write_json_file(file_path, sample_json_data)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    assert isinstance(data, dict)
    assert "name" in data
    assert "age" in data
    assert "active" in data


def test_yaml_file_content_structure(sample_yaml_data):
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp_file:
        file_path = temp_file.name

    write_yaml_file(file_path, sample_yaml_data)
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    assert isinstance(data, dict)
    assert "name" in data
    assert "age" in data
    assert "skills" in data
