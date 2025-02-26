import sys
import yaml
from functools import lru_cache
import os
import logging


Config: dict = {}

logger = logging.getLogger("paig_eval")

DEFAULT_CONFIG_PATH = 'conf'


@lru_cache
def load_config_file():
    config_file_path = os.path.join(os.path.dirname(__file__), os.path.join(DEFAULT_CONFIG_PATH, 'default_config.yaml'))
    if os.getenv('PAIG_EVAL_CONFIG_PATH') is not None:
        config_file_path = os.getenv('PAIG_EVAL_CONFIG_PATH')
    if not os.path.exists(config_file_path):
        sys.exit(f'No config file found at {config_file_path}')
    with open(config_file_path, 'r') as f:
        default_config = yaml.safe_load(f)
    return default_config