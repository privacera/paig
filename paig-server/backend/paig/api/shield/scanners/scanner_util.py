"""
This module provides functionality to parse configuration properties for scanners and recognizers.

Classes:
    Recognizer: Holds properties of a recognizer.

Functions:
    load_scanner: Loads scanner class based on provided information.
    parse_properties: Parses configuration properties to create scanner and recognizer objects.
    parse_section_indexes: Parses section indexes from section name.
    create_recognizer: Creates Recognizer objects based on configuration properties.
    get_recognizer_info: Extracts recognizer information from configuration.
    create_scanner: Creates scanner objects based on configuration properties.
    get_scanner_info: Extracts scanner information from configuration.

"""
import configparser
import importlib
import logging
import os.path
import re

from core.utils import format_to_root_path
from api.shield.scanners.BaseScanner import Scanner
from api.shield.scanners.PIIScanner import PIIScanner
from api.shield.utils.custom_exceptions import ShieldException
from api.shield.utils import config_utils

logger = logging.getLogger(__name__)


class Recognizer:
    """
    Recognizer class that holds the properties of a recognizer.
    """

    def __init__(self, name, enable, entity_type, ignore_list, detect_list, detect_regex, detect_list_score):
        """
        Initializes properties of a Recognizer object.

        Args:
            name (str): Name of the recognizer.
            enable (bool): Enable/disable flag for the recognizer.
            entity_type (str): Type of entity recognized by the recognizer.
            ignore_list (list): List of items to ignore during recognition.
            detect_list (list): List of items to detect.
            detect_regex (str): Regular expression for detection list.
        """
        self.name = name
        self.enable = enable
        self.entity_type = entity_type
        self.ignore_list = ignore_list
        self.detect_list = detect_list
        self.detect_regex = detect_regex
        self.detect_list_score = detect_list_score


def load_scanner(scanner_info):
    """
    Load scanner class based on provided information.

    Args:
        scanner_info (dict): Information about the scanner.

    Returns:
        Scanner: Loaded scanner object.
    """
    scanner_class_name = scanner_info['scanner_type'] if scanner_info.get('scanner_type') else scanner_info['name']

    try:
        module = importlib.import_module(f'api.shield.scanners.custom.{scanner_class_name}')
    except ModuleNotFoundError:
        module = importlib.import_module(f'api.shield.scanners.{scanner_class_name}')

    scanner_class = getattr(module, scanner_class_name)
    return scanner_class(**scanner_info)


def parse_properties(application_key) -> list[Scanner]:
    """
    Parse configuration properties to create scanner and recognizer objects.

    Args: application_key: Application key for accessing the configuration and to fetch the custom scanner props from
    portal.

    Returns:
        list: List of scanner objects.
    """
    scanner_objects = {}
    scanner_objects_list = []
    # Read Default properties file and create the scanner objects.
    scanner_objects = get_scanner_object_from_properties_file(default_properties=True, scanner_objects=scanner_objects)
    # Fetch custom properties from portal and create the scanner objects.
    scanner_objects = get_custom_scanner_objects_from_portal(default_properties=False, scanner_objects=scanner_objects,
                                                             application_key=application_key)

    for key in sorted(scanner_objects.keys()):
        if isinstance(scanner_objects[key], PIIScanner):
            scanner_objects[key].init_recognizers()
        scanner_objects_list.append(scanner_objects[key])

    return scanner_objects_list


def get_custom_scanner_objects_from_portal(default_properties, scanner_objects, application_key):
    config = configparser.ConfigParser()
    config.optionxform = str
    custom_properties_dict = {}
    config.read_dict(custom_properties_dict)
    scanner_objects = get_scanner_objects_based_on_config(config, default_properties, scanner_objects)
    return scanner_objects


def get_scanner_object_from_properties_file(default_properties, scanner_objects):
    config = configparser.ConfigParser()
    config.optionxform = str

    cust_file = config_utils.get_property_value("custom_scanner_properties_file", "api/shield/conf/shield_scanner.properties")
    cust_file_path = format_to_root_path(cust_file)
    default_file_path = format_to_root_path("api/shield/conf/shield_scanner.properties")

    if os.path.exists(cust_file_path):
        logger.debug(f"Reading scanner properties from {cust_file_path}")
        config.read(cust_file_path)
    elif os.path.exists(default_file_path):
        logger.debug(f"Reading scanner properties from {default_file_path}")
        config.read(default_file_path)
    else:
        logger.error(f"None of the Scanner config files i.e {cust_file_path}, {default_file_path} found")
        raise ShieldException(f"None of the Scanner config files i.e {cust_file_path}, {default_file_path} found")
    scanner_objects = get_scanner_objects_based_on_config(config, default_properties, scanner_objects)
    return scanner_objects


def get_scanner_objects_based_on_config(config, default_properties, scanner_objects):
    for section in config.sections():
        if section.startswith("scanner[") and '.' not in section:
            scanner_index = int(section.split("[")[1].split("]")[0])
            scanner_info = get_scanner_info(config, section)
            create_scanner(default_properties, scanner_index, scanner_info, scanner_objects)

        elif section.count('.') == 1 and section.startswith("scanner["):
            recognizer_index, scanner_index = parse_section_indexes(section)
            # TODO Need to finalise the mandatory properties and based on that we can set the fallback values
            recognizer_info = get_recognizer_info(config, section)
            create_recognizer(recognizer_index, recognizer_info, scanner_index, scanner_objects)
            recognizer_info.clear()

    return scanner_objects


def parse_section_indexes(section):
    """
    Parse section indexes from section name.

    Args:
        section (str): Section name.

    Returns:
        tuple: Recognizer index and scanner index.
    """
    section_list = section.split('.')
    scanner_index = int(section_list[0].split("[")[1].split("]")[0])
    recognizer_index = int(section_list[1].split("[")[1].split("]")[0])
    return recognizer_index, scanner_index


def create_recognizer(recognizer_index, recognizer_info, scanner_index, scanner_objects):
    """
    Create Recognizer objects based on configuration properties.

    Args:
        recognizer_index (int): Index of the recognizer.
        recognizer_info (dict): Information about the recognizer.
        scanner_index (int): Index of the scanner.
        scanner_objects (dict): Dictionary to hold scanner objects.
    """
    if recognizer_info['enable']:
        scanner_objects[scanner_index].recognizers[recognizer_index] = Recognizer(**recognizer_info)


def get_recognizer_info(config, section):
    """
    Extract recognizer information from configuration.

    Args:
        config (ConfigParser): Configuration parser object.
        section (str): Section name.

    Returns:
        dict: Recognizer information.
    """
    recognizer_info = {}
    try:
        recognizer_info = {
            'name': config.get(section, 'name', fallback=''),
            'enable': config.getboolean(section, 'enable', fallback=False),
            'entity_type': config.get(section, 'entity_type', fallback=''),
            'ignore_list': parse_keyword_list_value(config.get(section, 'ignore_list', fallback=[])),
            'detect_list': parse_keyword_list_value(config.get(section, 'detect_list', fallback=[])),
            'detect_regex': parse_regex_string_value(config.get(section, 'detect_regex', fallback=r'')),
            'detect_list_score': config.getfloat(section, 'detect_list_score', fallback=0.5)
        }
    except (configparser.NoOptionError, configparser.NoSectionError) as e:
        logger.error(f"Error parsing section '{section}': {e}")
    return recognizer_info


def parse_keyword_list_value(value):
    """
    Process keyword list value.

    Args:
        value (str): Keyword list value.

    Returns:
        list: List of keywords.
    """
    return value.split(",") if value else []


def parse_regex_string_value(value):
    """
    Process regex string value.

    Args:
        value (str): Regex string value.

    Returns:
        str: Raw Regex string.
    """
    try:
        # compile regex string to check for errors
        re.compile(value)
        return rf"{value}"
    except Exception as e:
        raise ShieldException(f"Error parsing regex string: {e}")


def create_scanner(default_predefined_properties, scanner_index, scanner_info, scanner_objects):
    """
    Create scanner objects based on configuration properties.

    Args:
        default_predefined_properties (bool): Flag indicating whether to use default or custom properties.
        scanner_index (int): Index of the scanner.
        scanner_info (dict): Information about the scanner.
        scanner_objects (dict): Dictionary to hold scanner objects.
    """
    if scanner_info['enable'] and scanner_index not in scanner_objects:
        if default_predefined_properties:
            scanner_objects[scanner_index] = load_scanner(scanner_info)
        else:
            load_nocode_scanners = config_utils.get_property_value_boolean('enable_nocode_scanners', False)
            if load_nocode_scanners:
                # Lazy initialization: Only create NoCodeScanner when required
                def create_nocode_scanner():
                    from api.shield.scanners.NoCodeScanner import NoCodeScanner
                    return NoCodeScanner(**scanner_info)

                scanner_objects[scanner_index] = create_nocode_scanner()
        logger.info(f"Loaded scanner: {scanner_objects[scanner_index].name}")


# Define the fallback values in a dictionary
FALLBACK_VALUES = {
    'model_path': '',
    'model_score_threshold': 0.5,
    'scanner_type': '',
    'entity_type': '',
    'model_entity_type_keyword': '',
    'model_input_max_length': 512,
    'model_input_truncation': True,
}


def get_scanner_info(config, section):
    """
    Extract scanner information from configuration.

    Args:
        config (ConfigParser): Configuration parser object.
        section (str): Section name.

    Returns:
        dict: Scanner information.
    """
    scanner_info = {}
    try:
        if config.has_section(section):
            for key, value in config.items(section):
                # Convert boolean, integer, or float types as needed
                if value.lower() in ('true', 'false'):
                    scanner_info[key] = config.getboolean(section, key)
                elif value.isdigit():
                    scanner_info[key] = config.getint(section, key)
                else:
                    try:
                        scanner_info[key] = config.getfloat(section, key)
                    except ValueError:
                        scanner_info[key] = value.split(',') if ',' in value else value

            # Handle fallback values for missing keys
            for key, fallback_value in FALLBACK_VALUES.items():
                if key not in scanner_info:
                    if isinstance(fallback_value, bool):
                        scanner_info[key] = config.getboolean(section, key, fallback=fallback_value)
                    elif isinstance(fallback_value, int):
                        scanner_info[key] = config.getint(section, key, fallback=fallback_value)
                    elif isinstance(fallback_value, float):
                        scanner_info[key] = config.getfloat(section, key, fallback=fallback_value)
                    else:
                        scanner_info[key] = config.get(section, key, fallback=fallback_value)
        else:
            raise configparser.NoSectionError(section)

    except (configparser.NoOptionError, configparser.NoSectionError) as e:
        logger.error(f"Error parsing section '{section}': {e}")
    return scanner_info
