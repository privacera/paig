import json
import os

import pytest

from paig_common.file_utils import FileUtils


@pytest.fixture(scope="module")
def temp_directory(tmpdir_factory):
    return tmpdir_factory.mktemp("test_data")


def test_get_file_paths_in_directory(temp_directory):
    # Create some temporary files
    file1 = temp_directory.join("file1.txt")
    file1.write("Test data")
    file2 = temp_directory.join("file2.txt")
    file2.write("More test data")

    # Call the method being tested
    file_paths = FileUtils.get_file_paths_in_directory(temp_directory)

    # Check the result
    assert len(file_paths) == 2
    assert file1 in file_paths
    assert file2 in file_paths


def test_load_json_from_file(temp_directory):
    # Create a temporary JSON file
    json_data = {"key": "value"}
    json_file = temp_directory.join("test.json")
    with open(json_file, "w") as f:
        json.dump(json_data, f)

    # Call the method being tested
    loaded_data = FileUtils.load_json_from_file(str(json_file))

    # Check the result
    assert loaded_data[0] == json.dumps(json_data)


def test_load_from_file(temp_directory):
    # Create a temporary JSON file
    json_data = [{"key": "value"}]
    json_file = temp_directory.join("test.json")
    with open(json_file, "w") as f:
        json.dump(json_data, f)

    # Call the method being tested
    loaded_data = FileUtils.read_json_file(str(json_file))

    # Check the result
    assert loaded_data == json_data


def test_append_json_to_file(temp_directory):
    # Create a temporary JSON file
    json_file = temp_directory.join("test.json")
    os.remove(str(json_file))

    # Append JSON data to the file
    data_to_append = {"new_key": "new_value"}
    FileUtils.append_json_to_file(str(json_file), data_to_append)

    # Read the file and check if data is appended correctly
    with open(json_file, "r") as f:
        appended_data = json.loads(f.read().strip())
    assert appended_data == data_to_append


def test_remove_line_from_file(temp_directory):
    # Create a temporary text file
    text_file = temp_directory.join("test.txt")
    with open(text_file, "w") as f:
        f.write('{"1": "1"}')
        f.write("\n")
        f.write('{"2": "2"}')
        f.write("\n")
        f.write('{"1": "1"}')
        f.write("\n")

    # Remove a line from the file
    FileUtils.remove_line_from_file(str(text_file), '{"2": "2"}')

    # Read the file and check if line is removed
    with open(text_file, "r") as f:
        lines = f.readlines()
    assert '{"2": "2"}' not in lines


def test_remove_empty_files(temp_directory):
    # Create some temporary files (including an empty file)
    file1 = temp_directory.join("file1.txt")
    file1.write("Test data")
    file2 = temp_directory.join("file2.txt")
    file2.write("")
    file3 = temp_directory.join("file3.txt")
    file3.write("More test data")

    # Remove empty files
    FileUtils.remove_empty_files(str(temp_directory))

    # Check if empty files are removed
    assert not os.path.exists(str(file2))
    assert os.path.exists(str(file1))
    assert os.path.exists(str(file3))
