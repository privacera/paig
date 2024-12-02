import pytest

from unittest.mock import patch, MagicMock

from core.utils import format_to_root_path
from api.shield.scanners.PIIScanner import PIIScanner
from api.shield.scanners.scanner_util import Recognizer
from presidio_analyzer import RecognizerResult
from api.shield.utils.custom_exceptions import ShieldException, UnsupportedFileTypeException


class TestPIIScanner:

    # note: the mock here is not used directly, but it is used inside the PIIScanner class
    @patch('api.shield.scanners.PIIScanner.PresidioAnalyzerEngine')
    def test_init_recognizers(self, mock_presidio_analyzer_engine):
        scanner = PIIScanner(name='name', request_types=['request_types'], enforce_access_control=True, model_path='model_path', model_threshold=0.5, entity_type='entity_type', enable=True)
        scanner.recognizers = {'recognizer1': Recognizer(name='recognizer1', enable=True, entity_type='entity_type',
                                                         ignore_list=['ignore1', 'ignore2'],
                                                         detect_list=['detect1', 'detect2'], detect_regex=r'',
                                                         detect_list_score=0.77)}
        scanner.init_recognizers()
        assert scanner.presidio_analyzer.analyzer.registry.add_recognizer.called

    def test_scan(self, mocker):
        recognizer_result_1 = RecognizerResult("PERSON", 3, 7, 0.85)
        recognizer_result_2 = RecognizerResult("EMAIL_ADDRESS", 36, 48, 1.0)
        analyzer_result_list = [recognizer_result_2, recognizer_result_1]
        side_effect = lambda prop: {
            "presidio_analyzer_score_threshold": 0.6,
        }.get(prop)
        mocker.patch('api.shield.utils.config_utils.get_property_value_float', side_effect=side_effect)

        scanner = PIIScanner(name='name', request_types=['request_types'], enforce_access_control=True, model_path='model_path', model_threshold=0.6, entity_type='entity_type', enable=True)
        message = 'Hi John, please send me an email to you@moon.com'
        result = scanner.scan(message)
        assert result.get('traits') == ['EMAIL_ADDRESS', 'PERSON']
        assert result.get('analyzer_result') == analyzer_result_list

    def test_load_recognizer_ignore_list(self):
        scanner = PIIScanner(name='name', request_types=['request_types'], enforce_access_control=True, model_path='model_path', model_threshold=0.5, entity_type='entity_type', enable=True)
        scanner.recognizers = {'recognizer1': Recognizer(name='recognizer1', enable=True, entity_type='entity_type',
                                                         ignore_list=['ignore1', 'ignore2'],
                                                         detect_list=['detect1', 'detect2'], detect_regex=r'',
                                                         detect_list_score=0.77)}
        result = scanner._load_recognizer_ignore_list()
        assert result == {'recognizer1': ['ignore1', 'ignore2']}

    def test_remove_ignore_list_keywords(self):
        scanner = PIIScanner(name='name', request_types=['request_types'], enforce_access_control=True, model_path='model_path', model_threshold=0.5, entity_type='entity_type', enable=True)
        analyzer_result_list = [
            MagicMock(start=0, end=4, entity_type='trait1', recognition_metadata={'recognizer_name': 'recognizer1'})]
        recognizer_ignore_dict = {'recognizer1': ['word']}
        result = scanner._remove_ignore_list_keywords(analyzer_result_list, recognizer_ignore_dict, 'word')
        assert result == []

    def test_load_keyword_list(self, mocker):
        # test when prop_val_list is a list
        prop_val_list = ['word1', 'word2']
        result = PIIScanner._load_keyword_list(prop_val_list)
        assert result == prop_val_list

        # test when prop_val_list is a file
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.getsize', return_value=10)
        mocker.patch('builtins.open', mocker.mock_open(read_data='word1\nword2\n'))
        prop_val_file = ['tests/data/ignore_list.txt']
        result = PIIScanner._load_keyword_list(prop_val_file)
        assert result == ['word1', 'word2']

        # test when prop_val_list is a csv file
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.getsize', return_value=10)
        mocker.patch('builtins.open', mocker.mock_open(read_data='word1,word2\n'))
        prop_val_file = ['tests/data/ignore_list.csv']
        result = PIIScanner._load_keyword_list(prop_val_file)
        assert result == ['word1', 'word2']

    def test_load_keyword_list_with_multiple_parameters(self, mocker):
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.getsize', return_value=10)

        def mock_open_func(file, mode='r'):
            if file == format_to_root_path('tests/data/ignore_list.txt'):
                return mocker.mock_open(read_data='word3\nword4\n').return_value
            elif file == format_to_root_path('tests/data/ignore_list.csv'):
                return mocker.mock_open(read_data='word5,word6\n').return_value

        mocker.patch('builtins.open', new=mock_open_func)

        prop_val_list = ['word1', 'word2', 'tests/data/ignore_list.txt', 'tests/data/ignore_list.csv']
        result = PIIScanner._load_keyword_list(prop_val_list)

        assert result == ['word1', 'word2', 'word3', 'word4', 'word5', 'word6']

    def test_load_keyword_list_error_case(self, mocker):
        # test when prop_val_list is a file but empty
        mocker.patch('builtins.open')
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.getsize', return_value=0)
        prop_val_file = ['tests/data/ignore_list.txt']
        with pytest.raises(ShieldException):
            PIIScanner._load_keyword_list(prop_val_file)

        # test when prop_val_list is a file but does not exist
        mocker.patch('os.path.exists', return_value=False)
        prop_val_file = ['tests/data/ignore_list.txt']
        with pytest.raises(FileNotFoundError):
            PIIScanner._load_keyword_list(prop_val_file)

        # test when prop_val_list is a file type is not valid
        mocker.patch('os.path.exists', return_value=True)
        mocker.patch('os.path.getsize', return_value=10)
        prop_val_file = ['tests/data/ignore_list.pdf']
        with pytest.raises(UnsupportedFileTypeException):
            PIIScanner._load_keyword_list(prop_val_file)
