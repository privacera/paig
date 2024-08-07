import pytest
from pydantic import ValidationError
from api.encryption.api_schemas.encryption_key import EncryptionKeyView, EncryptionKeyFilter
from api.encryption.database.db_models.encryption_key_model import EncryptionKeyType, EncryptionKeyStatus


def test_encryption_key_view_valid_data():
    valid_data = {
        "public_key": "public_key_value",
        "private_key": "private_key_value",
        "key_status": EncryptionKeyStatus.ACTIVE,
        "key_type": EncryptionKeyType.MSG_PROTECT_SHIELD
    }
    view = EncryptionKeyView(**valid_data)
    assert view.public_key == valid_data["public_key"]
    assert view.private_key == valid_data["private_key"]
    assert view.key_status == valid_data["key_status"]
    assert view.key_type == valid_data["key_type"]


def test_encryption_key_view_optional_fields():
    partial_data = {
        "public_key": "public_key_value"
    }
    view = EncryptionKeyView(**partial_data)
    assert view.public_key == partial_data["public_key"]
    assert view.private_key is None
    assert view.key_status is None
    assert view.key_type is None


def test_encryption_key_view_invalid_key_status():
    invalid_data = {
        "public_key": "public_key_value",
        "private_key": "private_key_value",
        "key_status": "INVALID_STATUS",
        "key_type": EncryptionKeyType.MSG_PROTECT_SHIELD
    }
    with pytest.raises(ValidationError):
        EncryptionKeyView(**invalid_data)


def test_encryption_key_view_invalid_key_type():
    invalid_data = {
        "public_key": "public_key_value",
        "private_key": "private_key_value",
        "key_status": EncryptionKeyStatus.ACTIVE,
        "key_type": "INVALID_TYPE"
    }
    with pytest.raises(ValidationError):
        EncryptionKeyView(**invalid_data)


def test_encryption_key_filter_valid_data():
    valid_data = {
        "key_status": "ACTIVE,PASSIVE",
        "key_type": EncryptionKeyType.MSG_PROTECT_SHIELD
    }
    filter_ = EncryptionKeyFilter(**valid_data)
    assert filter_.key_status == valid_data["key_status"]
    assert filter_.key_type == valid_data["key_type"]


def test_encryption_key_filter_optional_fields():
    partial_data = {
        "key_status": "ACTIVE"
    }
    filter_ = EncryptionKeyFilter(**partial_data)
    assert filter_.key_status == partial_data["key_status"]
    assert filter_.key_type is None


def test_encryption_key_filter_invalid_key_type():
    invalid_data = {
        "key_status": "ACTIVE",
        "key_type": "INVALID_TYPE"
    }
    with pytest.raises(ValidationError):
        EncryptionKeyFilter(**invalid_data)
