from unittest.mock import patch, call

import pytest
import configparser
from unittest import mock

from core.utils import format_to_root_path
from api.shield.scanners.scanner_util import (
    load_scanner,
    parse_properties,
    parse_section_indexes,
    create_recognizer,
    get_recognizer_info,
    create_scanner,
    get_scanner_info,
    parse_keyword_list_value,
    parse_regex_string_value,
    ShieldException, Recognizer,
    get_scanner_object_from_properties_file,
    get_scanner_objects_based_on_config
)


def test_load_scanner():
    scanner_info = {'name': 'PIIScanner', 'enable': True}
    with mock.patch('importlib.import_module') as mock_import_module:
        mock_module = mock.Mock()
        mock_import_module.side_effect = ModuleNotFoundError

        mock_scanner_class = mock.Mock()
        mock_module.PIIScanner = mock_scanner_class
        with pytest.raises(ModuleNotFoundError):
            load_scanner(scanner_info)
        mock_import_module.assert_called_with('api.shield.scanners.PIIScanner')


def test_load_scanner_custom():
    scanner_info = {'name': 'CustomScanner', 'enable': True}
    with mock.patch('importlib.import_module') as mock_import_module:
        mock_module = mock.Mock()
        mock_import_module.return_value = mock_module
        mock_scanner_class = mock.Mock()
        mock_module.CustomScanner = mock_scanner_class
        load_scanner(scanner_info)
        mock_import_module.assert_called_with('api.shield.scanners.custom.CustomScanner')
        mock_scanner_class.assert_called_with(**scanner_info)


def test_parse_properties():
    with mock.patch(
            'api.shield.scanners.scanner_util.get_scanner_object_from_properties_file') as mock_get_scanner_object_from_properties_file:
        with mock.patch(
                'api.shield.scanners.scanner_util.get_custom_scanner_objects_from_portal') as mock_get_custom_scanner_objects_from_portal:
            mock_scanner_objects = {1: mock.Mock()}
            mock_get_scanner_object_from_properties_file.return_value = mock_scanner_objects
            mock_get_custom_scanner_objects_from_portal.return_value = mock_scanner_objects
            result = parse_properties('app_key')
            assert result == [mock_scanner_objects[1]]
            mock_get_scanner_object_from_properties_file.assert_called_once()
            mock_get_custom_scanner_objects_from_portal.assert_called_once()


def test_parse_section_indexes():
    section = "scanner[1].recognizer[2]"
    recognizer_index, scanner_index = parse_section_indexes(section)
    assert recognizer_index == 2
    assert scanner_index == 1


def test_create_recognizer():
    # Create a mock scanner object with a recognizers attribute that is a dictionary
    scanner_objects = {1: mock.Mock()}
    scanner_objects[1].recognizers = {}

    recognizer_info = {
        'name': 'TestRecognizer',
        'enable': True,
        'entity_type': 'TEST',
        'ignore_list': 'ignore_list',
        'detect_list': ['detect'],
        'detect_regex': 'regex',
        'detect_list_score': 0.5
    }

    # Patch the Recognizer class to avoid creating actual Recognizer instances
    with mock.patch('api.shield.scanners.scanner_util.Recognizer', autospec=True) as mock_recognizer_class:
        create_recognizer(1, recognizer_info, 1, scanner_objects)

        # Check if the recognizer was created and assigned correctly
        mock_recognizer_class.assert_called_with(
            name='TestRecognizer',
            enable=True,
            entity_type='TEST',
            ignore_list='ignore_list',
            detect_list=['detect'],
            detect_regex='regex',
            detect_list_score=0.5
        )

        assert 1 in scanner_objects[1].recognizers
        assert scanner_objects[1].recognizers[1] == mock_recognizer_class.return_value


def test_get_recognizer_info():
    config = configparser.ConfigParser()
    config.read_dict({
        'scanner[1].recognizer[2]': {
            'name': 'TestRecognizer',
            'enable': 'yes',
            'entity_type': 'TEST',
            'ignore_list': 'ignore1,ignore2',
            'detect_list': 'detect1,detect2',
            'detect_regex': 'regex',
            'detect_list_score': '0.5'
        }
    })
    section = 'scanner[1].recognizer[2]'
    result = get_recognizer_info(config, section)
    assert result == {
        'name': 'TestRecognizer',
        'enable': True,
        'entity_type': 'TEST',
        'ignore_list': ['ignore1', 'ignore2'],
        'detect_list': ['detect1', 'detect2'],
        'detect_regex': r'regex',
        'detect_list_score': 0.5
    }


def test_create_scanner():
    scanner_objects = {}
    scanner_info = {
        'name': 'TestScanner',
        'enable': True,
        'request_types': ['request1'],
        'enforce_access_control': True,
        'model_path': 'path',
        'model_score_threshold': 0.5,
        'entity_type': 'TEST'
    }
    with mock.patch('api.shield.scanners.scanner_util.load_scanner') as mock_load_scanner:
        mock_scanner = mock.Mock()
        mock_load_scanner.return_value = mock_scanner
        create_scanner(True, 1, scanner_info, scanner_objects)
        assert scanner_objects[1] == mock_scanner


def test_get_scanner_info():
    config = configparser.ConfigParser()
    config.read_dict({
        'scanner[1]': {
            'name': 'TestScanner',
            'enable': 'True',
            'request_types': 'request1,request2',
            'enforce_access_control': 'True',
            'model_path': 'path',
            'model_score_threshold': '0.5',
            'entity_type': 'TEST',
            'model_entity_type_keyword': 'label',
            'scanner_type': 'NoCodeScanner',
            'model_input_max_length': '512',
            'model_input_truncation': 'True'
        }
    })
    section = 'scanner[1]'
    result = get_scanner_info(config, section)
    assert result == {
        'name': 'TestScanner',
        'enable': True,
        'request_types': ['request1', 'request2'],
        'enforce_access_control': True,
        'model_path': 'path',
        'model_score_threshold': 0.5,
        'entity_type': 'TEST',
        'model_entity_type_keyword': 'label',
        'scanner_type': 'NoCodeScanner',
        'model_input_max_length': 512,
        'model_input_truncation': True
    }


def test_parse_keyword_list_value():
    assert parse_keyword_list_value('item1,item2') == ['item1', 'item2']
    assert parse_keyword_list_value('') == []
    assert parse_keyword_list_value(None) == []


def test_parse_regex_string_value():
    assert parse_regex_string_value(r'\d+') == r'\d+'
    with pytest.raises(ShieldException):
        parse_regex_string_value(r'[')  # Invalid regex


def test_load_scanner_exception():
    scanner_info = {'name': 'NonExistentScanner', 'enable': True}
    with pytest.raises(ModuleNotFoundError):
        load_scanner(scanner_info)


def test_recognizer_class():
    _name = 'TestRecognizer'
    _enable = True
    _entity_type = 'TEST'
    _ignore_list = ['ignore1', 'ignore2']
    _detect_list = ['detect1', 'detect2']
    _detect_regex = r'regex'
    _detect_list_score = 0.5
    recognizer_object = Recognizer(
        name=_name,
        enable=_enable,
        entity_type=_entity_type,
        ignore_list=_ignore_list,
        detect_list=_detect_list,
        detect_regex=_detect_regex,
        detect_list_score=_detect_list_score
    )

    assert recognizer_object.name == _name
    assert recognizer_object.enable == _enable
    assert recognizer_object.entity_type == _entity_type
    assert recognizer_object.ignore_list == _ignore_list
    assert recognizer_object.detect_list == _detect_list
    assert recognizer_object.detect_regex == _detect_regex
    assert recognizer_object.detect_list_score == _detect_list_score


@patch('os.path.exists')
@patch('configparser.ConfigParser.read')
@patch('api.shield.scanners.scanner_util.get_scanner_objects_based_on_config')
def test_get_scanner_object_from_properties_file_with_existing_file(mock_get_scanner_objects_based_on_config, mock_read,
                                                                    mock_exists):
    # Mocking the os.path.exists to return True
    mock_exists.return_value = True
    # Mocking the get_scanner_objects_based_on_config to return a dictionary
    mock_get_scanner_objects_based_on_config.return_value = {'scanner': 'object'}
    # Call the function with the mocked objects
    result = get_scanner_object_from_properties_file(True, {})
    # Assert the function returns the expected result
    assert result == {'scanner': 'object'}
    # Assert the mocked functions were called with the correct arguments
    mock_exists.assert_called_once_with(format_to_root_path("api/shield/conf/shield_scanner.properties"))
    mock_read.assert_called_once_with(format_to_root_path("api/shield/conf/shield_scanner.properties"))
    mock_get_scanner_objects_based_on_config.assert_called_once()


@patch('os.path.exists')
@patch('api.shield.scanners.scanner_util.logger')
def test_get_scanner_object_from_properties_file_with_non_existing_file(mock_logger, mock_exists):
    # Mocking the os.path.exists to return False with random file name
    mock_exists.side_effect = lambda path: path == 'random_file.properties'
    # Call the function with the mocked objects and expect an Exception
    with pytest.raises(Exception):
        get_scanner_object_from_properties_file(True, {})
    # Assert the mocked functions were called with the correct arguments
    assert mock_exists.call_args_list == [call(format_to_root_path('api/shield/conf/shield_scanner.properties')),
                                          call(format_to_root_path('api/shield/conf/shield_scanner.properties'))]
    file_path = format_to_root_path('api/shield/conf/shield_scanner.properties')
    error_message = f"None of the Scanner config files i.e {file_path}, {file_path} found"
    mock_logger.error.assert_called_once_with(error_message)


@patch('api.shield.scanners.scanner_util.get_scanner_info')
@patch('api.shield.scanners.scanner_util.create_scanner')
def test_get_scanner_objects_based_on_config_with_scanner_section(mock_create_scanner, mock_get_scanner_info):
    # Mocking the get_scanner_info to return a dictionary
    mock_get_scanner_info.return_value = {'name': 'Scanner'}
    # Mocking the create_scanner to do nothing
    mock_create_scanner.return_value = None
    # Creating a ConfigParser object with a scanner section
    config = configparser.ConfigParser()
    config.add_section('scanner[1]')
    # Call the function with the mocked objects
    get_scanner_objects_based_on_config(config, True, {})
    # Assert the mocked functions were called with the correct arguments
    mock_get_scanner_info.assert_called_once()
    mock_create_scanner.assert_called_once()


@patch('api.shield.scanners.scanner_util.parse_section_indexes')
@patch('api.shield.scanners.scanner_util.get_recognizer_info')
@patch('api.shield.scanners.scanner_util.create_recognizer')
def test_get_scanner_objects_based_on_config_with_recognizer_section(mock_create_recognizer, mock_get_recognizer_info,
                                                                     mock_parse_section_indexes):
    # Mocking the parse_section_indexes to return a tuple
    mock_parse_section_indexes.return_value = (1, 1)
    # Mocking the get_recognizer_info to return a dictionary
    mock_get_recognizer_info.return_value = {'name': 'Recognizer'}
    # Mocking the create_recognizer to do nothing
    mock_create_recognizer.return_value = None
    # Creating a ConfigParser object with a recognizer section
    config = configparser.ConfigParser()
    config.add_section('scanner[1].recognizer[1]')
    # Call the function with the mocked objects
    get_scanner_objects_based_on_config(config, True, {})
    # Assert the mocked functions were called with the correct arguments
    mock_parse_section_indexes.assert_called_once()
    mock_get_recognizer_info.assert_called_once()
    mock_create_recognizer.assert_called_once()
