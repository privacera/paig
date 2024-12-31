import json
import yaml

def read_json_file(file_path):
    """
    Reads a JSON file and returns the content as a Python dictionary.
    :param file_path: Path to the JSON file
    :return: Python dictionary representing the JSON content
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(file_path, data):
    """
    Writes a Python dictionary to a JSON file.
    :param file_path: Path to the JSON file
    :param data: Python dictionary to write
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def read_yaml_file(file_path):
    """
    Reads a YAML file and returns the content as a Python dictionary.
    :param file_path: Path to the YAML file
    :return: Python dictionary representing the YAML content
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def write_yaml_file(file_path, data):
    """
    Writes a Python dictionary to a YAML file.
    :param file_path: Path to the YAML file
    :param data: Python dictionary to write
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False)
