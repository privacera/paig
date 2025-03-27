import os
import sys
import yaml
import logging
import re
from functools import lru_cache
from core.utils import recursive_merge_dicts, normalize_path  # Import normalize_path from utils
from core import constants


Config: dict = {}
logger = logging.getLogger(__name__)
DEFAULT_CONFIG_PATH = 'configs'

def replace_pattern_with_env(yaml_str):
    """Replace ${ENV_VARIABLE} with actual environment variable values."""
    pattern = r'\$\{{(\w+)\}}'
    
    def replace(match):
        env_var_name = match.group(1)
        raw_value = os.environ.get(env_var_name, match.group(0))
        return normalize_path(raw_value)  # Directly return the normalized value
    
    return re.sub(pattern, replace, yaml_str)

@lru_cache
def load_config_file():
    """Load and merge YAML config files, handling OS-specific paths."""
    
    raw_config_path = os.getenv('CONFIG_PATH', DEFAULT_CONFIG_PATH)
    config_path = normalize_path(raw_config_path)
    
    raw_custom_config_path = os.getenv('EXT_CONFIG_PATH', "")
    custom_config_path = normalize_path(raw_custom_config_path)
    
    env = os.getenv('SECURE_CHAT_DEPLOYMENT', 'default')

    raw_default_config_file = os.path.join(config_path, 'default_config.yaml')
    default_config_file = normalize_path(raw_default_config_file)
    
    if constants.MODE == 'standalone':
        raw_default_config_file = os.path.join(config_path, 'standalone_config.yaml')
        default_config_file = normalize_path(raw_default_config_file)
        
    if not os.path.exists(default_config_file):
        sys.exit(f'No default config file found at {default_config_file}')

    with open(default_config_file, 'r') as f:
        yaml_str = f.read()

    yaml_str_modified = replace_pattern_with_env(yaml_str)
    default_config = yaml.safe_load(yaml_str_modified)

    raw_custom_config_file = os.path.join(config_path, f'{env}_config.yaml')
    custom_config_file = normalize_path(raw_custom_config_file)
    
    if custom_config_path and os.path.exists(os.path.join(custom_config_path, f'{env}_config.yaml')):
        raw_custom_config_file = os.path.join(custom_config_path, f'{env}_config.yaml')
        custom_config_file = normalize_path(raw_custom_config_file)
     
    if os.path.exists(custom_config_file) and custom_config_file != default_config_file:
        logger.info(f'Found custom config at {custom_config_file}')
        with open(custom_config_file, 'r') as f:
            custom_config = yaml.safe_load(f)
        if custom_config and isinstance(custom_config, dict):
            default_config = recursive_merge_dicts(default_config, custom_config)

    logger.info(f"Final config: {default_config}")
    return default_config
