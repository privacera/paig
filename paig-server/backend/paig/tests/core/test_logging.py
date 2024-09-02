from core.logging_init import get_logs_directory, set_logging_level, get_logging_config
import pytest
import os
from core import logging_init
import shutil


def test_get_logs_directory_default():
    env_log_path = os.getenv('LOG_PATH')
    log_path = get_logs_directory()
    assert log_path == env_log_path


def test_get_logs_directory_with_default_log_dir():
    current_log_path = os.getenv('LOG_PATH')
    os.environ.pop('LOG_PATH')
    current_log_dir = logging_init.DEFAULT_LOG_PATH
    logging_init.DEFAULT_LOG_PATH = "tests/temp_log_dir"
    os.makedirs("tests/temp_log_dir", exist_ok=True)
    assert get_logs_directory() == "tests/temp_log_dir"
    shutil.rmtree("tests/temp_log_dir")
    logging_init.DEFAULT_LOG_PATH = current_log_dir
    if current_log_path:
        os.environ['LOG_PATH'] = current_log_path


def test_get_logs_directory_creating_default_log_dir():
    current_log_path = os.getenv('LOG_PATH')
    os.environ.pop('LOG_PATH')
    current_log_dir = logging_init.DEFAULT_LOG_PATH
    logging_init.DEFAULT_LOG_PATH = "tests/temp_log_dir"
    assert get_logs_directory() == "tests/temp_log_dir"
    shutil.rmtree("tests/temp_log_dir")
    logging_init.DEFAULT_LOG_PATH = current_log_dir
    if current_log_path:
        os.environ['LOG_PATH'] = current_log_path


def test_get_logs_directory_with_invalid_log_path():
    current_log_path = os.getenv('LOG_PATH')
    os.environ['LOG_PATH'] = 'invalid'
    with pytest.raises(SystemExit) as e:
        get_logs_directory()
    if current_log_path:
        os.environ['LOG_PATH'] = current_log_path
    assert str(e.value) != None


def test_get_logging_config():
    logging_ini_file_path = get_logging_config()
    assert logging_ini_file_path == os.path.join(os.environ['CONFIG_PATH'], "logging.ini")


def test_get_logging_config_with_default_config_path():
    current_config_path = os.getenv('CONFIG_PATH')
    os.environ.pop('CONFIG_PATH')
    logging_ini_file_path = get_logging_config()
    assert logging_ini_file_path == os.path.join(logging_init.DEFAULT_LOGGING_CONFIG_PATH, "logging.ini")
    if current_config_path:
        os.environ['CONFIG_PATH'] = current_config_path


def test_get_logging_config_with_invalid_config_path():
    current_config_path = os.getenv('CONFIG_PATH')
    os.environ['CONFIG_PATH'] = 'invalid'
    with pytest.raises(SystemExit) as e:
        get_logging_config()
    if current_config_path:
        os.environ['CONFIG_PATH'] = current_config_path
    assert str(e.value) != None


def test_set_logging_level():
    set_logging_level("debug")
    set_logging_level("error")
    set_logging_level("info")
    with pytest.raises(SystemExit) as e:
        set_logging_level("invalid")
    assert str(e.value) != None
