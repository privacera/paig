import csv
import os.path
import logging

from core.utils import format_to_root_path
from api.shield.model.analyzer_result import AnalyzerResult
from api.shield.scanners.BaseScanner import Scanner
from api.shield.presidio.presidio_analyzer_engine import PresidioAnalyzerEngine
from presidio_analyzer import PatternRecognizer, Pattern

from api.shield.utils.custom_exceptions import ShieldException, UnsupportedFileTypeException

logger = logging.getLogger(__name__)
unsupported_file_types = [
    # Data Files
    "json",
    "xml",
    "yaml", "yml",
    "tsv",
    "ini",
    "log",

    # Document Files
    "pdf",
    "doc", "docx",
    "xls", "xlsx",
    "ppt", "pptx",
    "odt",
    "ods",
    "odp",

    # Image Files
    "jpg", "jpeg",
    "png",
    "gif",
    "bmp",
    "tiff",
    "svg",
    "webp",

    # Audio Files
    "mp3",
    "wav",
    "flac",
    "aac",
    "ogg",

    # Video Files
    "mp4",
    "mkv",
    "avi",
    "mov",
    "wmv",
    "flv",
    "webm",

    # Archive Files
    "zip",
    "rar",
    "tar",
    "gz",
    "7z",

    # Code Files
    "py",  # Python
    "java",  # Java
    "cpp", "h",  # C++
    "c", "h",  # C
    "js",  # JavaScript
    "html",  # HTML
    "css",  # CSS
    "php",  # PHP
    "rb",  # Ruby
    "go",  # Go
    "rs",  # Rust
    "sh",  # Shell Script

    # Configuration Files
    "conf",
    "cfg",
    "properties",

    # Miscellaneous
    "md",  # Markdown
    "rtf",  # Rich Text Format

    # Specialized
    "sql",  # SQL Script
    "db",  # Database File
    "apk",  # Android Package
    "exe",  # Executable File
    "dll",  # Dynamic Link Library
    "iso"  # Disc Image File
]


def build_analyzer_result(analyzer_result_list, model_name, scanner_name):
    """
    Build the analyzer result from the list of RecognizerResult
    :param scanner_name:
    :param model_name:
    :param analyzer_result_list:
    :return: refined analyzer result list
    """
    refined_analyzer_results = []
    for result in analyzer_result_list:
        analyzer_result = AnalyzerResult(start=result.start, end=result.end, entity_type=result.entity_type,
                                         score=result.score, model_name=model_name,
                                         scanner_name=scanner_name,
                                         analysis_explanation=result.analysis_explanation,
                                         recognition_metadata=result.recognition_metadata)
        refined_analyzer_results.append(analyzer_result)
    return refined_analyzer_results


class PIIScanner(Scanner):
    """
    Scanner implementation for detecting PII in the input prompt.
    """

    def __init__(self, name, request_types, enforce_access_control, model_path, model_score_threshold, entity_type,
                 enable, **kwargs):
        """
        Initialize the required models and variables for the scanner
        """
        super().__init__(name, request_types, enforce_access_control, model_path, model_score_threshold, entity_type,
                         enable, **kwargs)

        self.presidio_analyzer = PresidioAnalyzerEngine()
        self.recognizers = {}
        self.recognizer_ignore_dict = {}

    def init_recognizers(self):
        self._add_custom_recognizers()
        # check if there's any traits to ignore
        self.recognizer_ignore_dict = self._load_recognizer_ignore_list()

    def scan(self, message: str) -> dict:
        """
        Process and sanitize the input prompt according to the specific scanner's implementation.

        Parameters:
            message (str): The input prompt that needs to be processed.

        Returns:
            dict: dictionary consisting of tags and other additional infos
        """

        # analyze the prompt using the presidio analyzer
        analyzer_result_list = self.presidio_analyzer.analyze(message)
        refined_analyzer_results = build_analyzer_result(analyzer_result_list, model_name=self.model_path,
                                                         scanner_name=self.name)

        logger.debug(f"Analyzer result after scanning the message : {refined_analyzer_results}")

        # remove the ignore list keywords from the analyzer result list
        if self.recognizer_ignore_dict:
            refined_analyzer_results = self._remove_ignore_list_keywords(refined_analyzer_results,
                                                                         self.recognizer_ignore_dict,
                                                                         message)

        # get only the traits from the analyzer result
        traits = set([result.entity_type for result in refined_analyzer_results])

        return {"traits": traits, "analyzer_result": refined_analyzer_results}

    def _load_recognizer_ignore_list(self):
        recognizer_ignore_dict = {}
        for key, value in self.recognizers.items():
            ignore_list = self._load_keyword_list(value.ignore_list)
            if ignore_list:
                recognizer_ignore_dict[value.name] = ignore_list
        return recognizer_ignore_dict

    def _add_custom_recognizers(self):
        """
        Add custom recognizers to the presidio analyzer
        :return: None
        """
        logger.debug("Adding custom recognizers to presidio registry")
        logger.debug(f"Found {len(self.recognizers)} custom recognizers")
        for key, value in self.recognizers.items():

            detect_list = self._load_keyword_list(value.detect_list)

            # check if the regex pattern is provided
            detect_regex_pattern = None
            if value.detect_regex:
                detect_regex_pattern = [Pattern(name="detect_regex", regex=value.detect_regex,
                                                score=value.detect_list_score)]
            # create custom recognizer
            _custom_recognizer = PatternRecognizer(name=value.name,
                                                   supported_entity=value.entity_type,
                                                   deny_list=detect_list,
                                                   deny_list_score=value.detect_list_score,
                                                   patterns=detect_regex_pattern)

            # add custom recognizer to presidio analyzer recognizer registry
            self.presidio_analyzer.analyzer.registry.add_recognizer(_custom_recognizer)

    @staticmethod
    def _remove_ignore_list_keywords(analyzer_result_list, recognizer_ignore_dict, message):
        """
        Remove the ignore list keywords from the analyzer result list
        :param analyzer_result_list: list of RecognizerResult
        :param recognizer_ignore_dict: list of keywords to ignore for each recognizer
        :param message: input prompt
        :return: list of RecognizerResult
        """
        logger.debug("Removing ignore list keywords from the analyzer result list")
        new_analyzer_result_list = []
        logger.debug(f"Recognizer and its corresponding ignore list:\n{recognizer_ignore_dict}")

        for result in analyzer_result_list:
            _result_word = message[result.start: result.end]
            _result_recognizer_name = result.recognition_metadata.get("recognizer_name")

            logger.debug(f"Checking word: {_result_word} identified by recognizer: {_result_recognizer_name}")
            # if the word is not specified to be allowed for the given recognizer, keep in the PII entities
            if (_result_recognizer_name not in recognizer_ignore_dict or
                    _result_word not in recognizer_ignore_dict[_result_recognizer_name]):
                new_analyzer_result_list.append(result)
                logger.debug(f"Added word: {_result_word} identified by recognizer: {_result_recognizer_name}")

        return new_analyzer_result_list

    @staticmethod
    def _load_keyword_list(prop_value) -> list:
        """
        Load the keyword list from the file.
        :param prop_value: List of file paths or keywords.
        :return: List of keywords.
        """
        keyword_list = []
        logger.debug(f"Loading keyword list: {prop_value}")
        if prop_value:
            for prop in prop_value:
                prop = prop.strip()
                file_type, is_file_path = validate_and_get_file_type(prop)
                if is_file_path:
                    keyword_list.extend(_get_list_from_file(format_to_root_path(prop), file_type))
                else:
                    keyword_list.append(prop)
        return keyword_list


def _get_list_from_file(file_name, file_type) -> list:
    """
    Read the file and return the list of keywords
    :param file_name:
    :param file_type: The type of the file ('txt' or 'csv').
    :return: list of keywords
    """
    logger.debug(f"Loading keyword list from file {file_name}")
    data = []
    try:
        with open(file_name, 'r') as file:
            if file_type == 'txt':
                for line in file:
                    data.append(line.strip())  # Assuming each line is a separate element
            elif file_type == 'csv':
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    data.extend(row)
    except Exception as e:
        raise ShieldException(f"Error reading file {file_name}. Error: {e}")
    return data


def validate_non_empty_file(file_name):
    """
    Validates if the file is not empty. Raises an exception if the file is empty.
    :param file_name: Path of the file to check.
    """
    if os.path.getsize(file_name) == 0:
        logger.error(f"The given file {file_name} is empty")
        raise ShieldException(f"The given file {file_name} is empty")


def validate_and_get_file_type(file_path):
    """
    Check if the provided string is a valid file path and determine its type.
    :param file_path: The file path to check
    :return: tuple (file_type, is_file_path) where file_type is 'txt', 'csv', or None, and is_file_path is True or False
    """
    supported_file_types = ['txt', 'csv']
    file_type = file_path.split('.')[-1]
    if file_type in unsupported_file_types:
        logger.error(f"Unsupported file type for file: {file_path}")
        raise UnsupportedFileTypeException(f"Unsupported file type for file: {file_path}")
    elif file_type in supported_file_types:
        file_path = format_to_root_path(file_path)
        validate_file_path_exists(file_path)
        validate_non_empty_file(file_path)
        return file_type, True

    return None, False


def validate_file_path_exists(file_path):
    """
    Check if the file path exists. Raises an exception if the file does not exist.
    :param file_path:
    :return:
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        raise FileNotFoundError(f"File does not exist: {file_path}")
