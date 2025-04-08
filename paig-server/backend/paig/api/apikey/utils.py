from datetime import datetime, timezone
from core.config import load_config_file
from typing import Union, List
from enum import Enum
import secrets
import uuid


conf = load_config_file()


def generate_hex_key(length: int = 22):
    return secrets.token_hex(length)[:length]

def short_uuid():
    return f"{uuid.uuid4().int % (36**10):010x}"  # 13-char base36



def convert_token_expiry_to_epoch_time(token_expiry) -> int:
    # Convert token expiry time to epoch time
    return int(token_expiry.timestamp())


def get_default_token_expiry_epoch_time() -> int:
    # Get default token expiry time
    api_key_config = conf.get('api_key')
    expire_days = api_key_config.get('expire_days', 365)
    current_epoch = int(datetime.now(timezone.utc).timestamp())
    max_valid_epoch = current_epoch + expire_days * 24 * 60 * 60
    return max_valid_epoch


def validate_token_expiry_time(token_expiry: int) -> int:
    # Validate token expiry time is in between 1 year from current time to one year max
    api_key_config = conf.get('api_key')
    expire_days = api_key_config.get('expire_days', 365)
    current_epoch = int(datetime.now(timezone.utc).timestamp())
    max_valid_epoch = current_epoch + expire_days * 24 * 60 * 60  # 1 year in seconds

    if token_expiry > max_valid_epoch or token_expiry < current_epoch:
        return False
    return True


def normalize_parameter(param: Union[str, List[str]]) -> List[str]:
    """
    Normalize query param that may be a comma-separated string or a list.
    """
    if isinstance(param, list) and len(param) == 1 and isinstance(param[0], str):
        return [s.strip() for s in param[0].split(",") if s.strip()]
    if isinstance(param, str):
        return [s.strip() for s in param.split(",") if s.strip()]
    return param if isinstance(param, list) else []


class EncryptionKeyStatus(Enum):
    ACTIVE = "ACTIVE"
    PASSIVE = 'PASSIVE'
    DISABLED = "DISABLED"
    DELETED = "DELETED"


class APIKeyStatus(Enum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    DELETED = "DELETED"