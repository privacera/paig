import re
import pytest
from datetime import datetime, timezone

from api.apikey.utils import (
    generate_hex_key, short_uuid, 
    convert_token_expiry_to_epoch_time, 
    get_default_token_expiry_epoch_time,
    validate_token_expiry_time, 
    normalize_parameter,
    EncryptionKeyStatus,
    APIKeyStatus
)


def test_generate_hex_key_length():
    key = generate_hex_key(16)
    assert isinstance(key, str)
    assert len(key) == 16
    assert re.fullmatch(r"[a-f0-9]+", key)


def test_short_uuid_format_and_length():
    uid = short_uuid()
    assert isinstance(uid, str)
    assert uid is not None
    assert re.fullmatch(r"[a-f0-9]+", uid)


def test_convert_token_expiry_to_epoch_time():
    now = datetime.now(timezone.utc)
    epoch = convert_token_expiry_to_epoch_time(now)
    assert isinstance(epoch, int)
    assert abs(epoch - int(now.timestamp())) < 2


def test_get_default_token_expiry_epoch_time():
    result = get_default_token_expiry_epoch_time()
    now = int(datetime.now(timezone.utc).timestamp())
    # Should be approx 365 days from now
    assert result > now
    assert (result - now) // (24 * 60 * 60) in (364, 365, 366)


def test_validate_token_expiry_time_valid():
    future = int(datetime.now(timezone.utc).timestamp()) + 10
    assert validate_token_expiry_time(future) is True


def test_validate_token_expiry_time_expired():
    past = int(datetime.now(timezone.utc).timestamp()) - 100
    assert validate_token_expiry_time(past) is False


def test_validate_token_expiry_time_too_far():
    far_future = int(datetime.now(timezone.utc).timestamp()) + (366 * 24 * 60 * 60)
    assert validate_token_expiry_time(far_future) is False


@pytest.mark.parametrize("input_param,expected", [
    ("val1,val2 , val3", ["val1", "val2", "val3"]),
    (["val1, val2"], ["val1", "val2"]),
    (["val1", "val2"], ["val1", "val2"]),
    ("", []),
    ([], []),
    (None, []),
])
def test_normalize_parameter(input_param, expected):
    result = normalize_parameter(input_param)
    assert result == expected


def test_encryption_key_status_enum():
    assert EncryptionKeyStatus.ACTIVE.value == "ACTIVE"
    assert EncryptionKeyStatus.DELETED.name == "DELETED"


def test_api_key_status_enum():
    assert APIKeyStatus.ACTIVE.value == "ACTIVE"
    assert APIKeyStatus.DISABLED.name == "DISABLED"
