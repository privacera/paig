import logging
import logging.config
import configparser
import os
import sys

DEFAULT_LOG_PATH = "securechat/logs"
DEFAULT_LOGGING_CONFIG_PATH = 'configs/'
LOG_FILE = "securechat.log"
ACCESS_LOG_FILE = "securechat_access.log"
LOGGING_CONFIG = "logging.ini"
LOG_FILE_HANDLER = "handler_logfile"
ACCESS_FILE_HANDLER = "handler_access_file"
ARGS = "args"


def get_logs_directory() -> str:
    if 'LOG_PATH' not in os.environ:
        if os.path.isdir(DEFAULT_LOG_PATH):
            print(f"Custom LOG_PATH not found. Using default Log Directory :- {DEFAULT_LOG_PATH}")
            return DEFAULT_LOG_PATH
        else:
            print(f"Creating default log directory:- {DEFAULT_LOG_PATH}")
            os.makedirs(DEFAULT_LOG_PATH)
            print(f"Custom LOG_PATH not found. Using default Log Directory :- {DEFAULT_LOG_PATH}")
            return DEFAULT_LOG_PATH
    else:
        custom_log_path = os.getenv('LOG_PATH')
        if not os.path.isdir(custom_log_path):
            print(f"Invalid Custom LOG_PATH:- {custom_log_path}, Set valid LOG_PATH as environment variable")
            sys.exit(f"Invalid Custom LOG_PATH:- {custom_log_path}, Set valid LOG_PATH as environment variable")
        else:
            print(f"Custom LOG_PATH found. Using custom Log directory  :- {custom_log_path}")
            return custom_log_path


def get_logging_config():
    if 'CONFIG_PATH' not in os.environ:
        logging_config_path = os.path.join(DEFAULT_LOGGING_CONFIG_PATH, LOGGING_CONFIG)
        print(f"Using default logging config:- {logging_config_path}")
    else:
        config_path = os.getenv('CONFIG_PATH')
        logging_config_path = os.path.join(config_path, LOGGING_CONFIG)
        print(f"Using custom logging config:- {logging_config_path}")
    if os.path.isfile(logging_config_path):
        return logging_config_path
    else:
        print(f"Logging config file not found at:- {logging_config_path}")
        sys.exit(f"Logging config file not found at:- {logging_config_path}")


def get_log_handler_args(config, handler, log_path):
    log_handler_args = config.get(handler, ARGS)
    return log_handler_args.replace('{log_file_name}', log_path)


def set_logging():
    log_directory = get_logs_directory()
    logging_config = get_logging_config()
    log_file_path = os.path.join(log_directory, LOG_FILE)
    access_logfile_path = os.path.join(log_directory, ACCESS_LOG_FILE)
    config = configparser.ConfigParser()
    config.read(logging_config)
    log_file_args = get_log_handler_args(config, LOG_FILE_HANDLER, log_file_path)
    access_log_file_args = get_log_handler_args(config, ACCESS_FILE_HANDLER, access_logfile_path)
    config.set(LOG_FILE_HANDLER, ARGS, log_file_args)
    config.set(ACCESS_FILE_HANDLER, ARGS, access_log_file_args)
    print(f"Log file path set as:- {log_file_path}")
    print(f"Access Log file path set as:- {access_logfile_path}")
    logging.config.fileConfig(config)


def set_logging_level(log_level: str):
    log_level = log_level.lower()
    logger = logging.getLogger()
    if log_level == "debug":
        logger.setLevel(logging.DEBUG)
    elif log_level == "info":
        logger.setLevel(logging.INFO)
    elif log_level == "error":
        logger.setLevel(logging.ERROR)
    else:
        print(f"Log level {log_level} is invalid, log level DEBUG, INFO and ERROR supported.")
        sys.exit(f"Log level {log_level} is invalid, log level DEBUG, INFO and ERROR supported.")