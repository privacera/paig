import sys
import yaml
from functools import lru_cache
import os
import logging
from core.utils import recursive_merge_dicts
import re
from core import constants

Config: dict = {}

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = 'configs'


# Define a function to search and replace patterns in YAML string
def replace_pattern_with_env(yaml_str):
    # Define the pattern to search for (e.g., ${ENV_VARIABLE})
    pattern = r'\$\{{(\w+)\}}'

    # Define a function to replace the pattern with the corresponding environment variable value
    def replace(match):
        env_var_name = match.group(1)
        # Check if the environment variable exists
        if env_var_name in os.environ:
            return os.environ[env_var_name]
        else:
            # If the environment variable doesn't exist, keep the original pattern
            return match.group(0)

    # Perform the replacement
    yaml_str_modified = re.sub(pattern, replace, yaml_str)
    return yaml_str_modified


@lru_cache
def load_config_file():
    config_path = os.getenv('CONFIG_PATH')
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    custom_config_path = os.getenv('EXT_CONFIG_PATH')
    env = os.getenv('SECURE_CHAT_DEPLOYMENT')
    default_config_file = os.path.join(config_path, 'default_config.yaml')
    if constants.MODE == 'standalone':
        default_config_file = os.path.join(config_path, 'standalone_config.yaml')
    if not os.path.exists(default_config_file):
        sys.exit(f'No default config file found at {default_config_file}')

    with open(default_config_file, 'r') as f:
        yaml_str = f.read()
        # default_config = yaml.safe_load(f)

    # Perform search and replace with environment variables
    yaml_str_modified = replace_pattern_with_env(yaml_str)

    # Load modified YAML document
    default_config = yaml.safe_load(yaml_str_modified)

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
