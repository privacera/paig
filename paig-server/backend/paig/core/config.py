import json
import sys
import yaml
from functools import lru_cache
import os
import logging
from core.utils import recursive_merge_dicts, format_to_root_path


Config: dict = {}

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = 'conf'
DEFAULT_AI_APP_CONFIG = 'ai_application_defaults_for_demo_app.json'


@lru_cache
def load_config_file():
    config_path = os.getenv('CONFIG_PATH')
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    custom_config_path = os.getenv('EXT_CONFIG_PATH')
    env = os.getenv('PAIG_DEPLOYMENT')
    default_config_file = os.path.join(config_path, 'default_config.yaml')
    if not os.path.exists(default_config_file):
        sys.exit(f'No default config file found at {default_config_file}')

    with open(default_config_file, 'r') as f:
        default_config = yaml.safe_load(f)

    # Load file from custom config path if provided
    custom_config_file = os.path.join(config_path, f'{env}_config.yaml')
    if custom_config_path is not None:
        logger.info(f'Custom config directory provided:- {custom_config_path}')
        if os.path.exists(os.path.join(custom_config_path, f'{env}_config.yaml')):
            custom_config_file = os.path.join(custom_config_path, f'{env}_config.yaml')
    logger.info(f'Looking for custom config at path {custom_config_path}')

    if os.path.exists(custom_config_file) and custom_config_file != default_config_file:
        logger.info(f'Found custom config at path {custom_config_file}')
        with open(custom_config_file, 'r') as f:
            custom_config = yaml.safe_load(f)
        if custom_config is not None and isinstance(custom_config, dict):
            default_config = recursive_merge_dicts(default_config, custom_config)
        else:
            logger.info(f'No valid configuration found in custom config file {custom_config_file}')
    else:
        logger.info(f'No custom config file found at {custom_config_file}')
    logger.info(f"{default_config}")
    return default_config


@lru_cache()
def load_default_ai_config():
    config_path = os.getenv('CONFIG_PATH')
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    ai_config_file = os.path.join(config_path, DEFAULT_AI_APP_CONFIG)
    custom_config_path = os.getenv('EXT_CONFIG_PATH')
    if custom_config_path and os.path.exists(os.path.join(custom_config_path, DEFAULT_AI_APP_CONFIG)):
        ai_config_file = os.path.join(custom_config_path, DEFAULT_AI_APP_CONFIG)
    logger.info(f'Default AI config file path is {ai_config_file}')
    with open(ai_config_file, 'r') as f:
        ai_app_conf = json.load(f)
    return ai_app_conf


@lru_cache
def get_version():
    with open(os.path.join(format_to_root_path('VERSION'))) as file:
        for line in file:
            if line.startswith('__version__'):
                # Extract the version value from the line
                version = line.split('=')[1].strip().strip("'\"")
                return version
    raise ValueError("Version not found")
