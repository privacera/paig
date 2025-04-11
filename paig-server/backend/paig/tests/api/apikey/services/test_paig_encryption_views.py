import pytest
from api.apikey.services.paig_encryption_views import (
    LevelEncryptionKeyBaseView,
    PaigLevel1EncryptionKeyView,
    PaigLevel2EncryptionKeyView,
)


def test_level_encryption_key_base_view_fields():
    data = {
        "keyId": "key-123",
        "createdById": "user-1",
        "updatedById": "user-2",
        "keyStatus": "ACTIVE"
    }
    obj = LevelEncryptionKeyBaseView(**data)
    assert obj.key_id == "key-123"
    assert obj.created_by_id == "user-1"
    assert obj.updated_by_id == "user-2"
    assert obj.key_status == "ACTIVE"

    # check serialization
    serialized = obj.model_dump(by_alias=True)
    assert serialized["keyId"] == "key-123"
    assert serialized["createdById"] == "user-1"
    assert serialized["updatedById"] == "user-2"
    assert serialized["keyStatus"] == "ACTIVE"


def test_paig_level1_encryption_key_view_fields():
    data = {
        "keyId": "key-001",
        "createdById": "creator-001",
        "updatedById": "updator-001",
        "keyStatus": "ACTIVE",
        "Level1KeyValue": "level1-secret"
    }
    obj = PaigLevel1EncryptionKeyView(**data)
    assert obj.key_id == "key-001"
    assert obj.paig_key_value == "level1-secret"

    # Check alias on dump
    assert obj.model_dump(by_alias=True)["Level1KeyValue"] == "level1-secret"


def test_paig_level2_encryption_key_view_fields():
    data = {
        "keyId": "key-002",
        "createdById": "creator-002",
        "updatedById": "updator-002",
        "keyStatus": "INACTIVE",
        "Level2KeyValue": "level2-secret"
    }
    obj = PaigLevel2EncryptionKeyView(**data)
    assert obj.key_id == "key-002"
    assert obj.paig_key_value == "level2-secret"

    # Check alias on dump
    assert obj.model_dump(by_alias=True)["Level2KeyValue"] == "level2-secret"


def test_missing_optional_fields():
    obj = LevelEncryptionKeyBaseView()
    assert obj.key_id is None
    assert obj.created_by_id is None
    assert obj.updated_by_id is None
    assert obj.key_status is None


def test_inheritance_from_base_view():
    # Assuming BaseView has an attribute like 'created_at' or similar
    assert issubclass(PaigLevel1EncryptionKeyView, LevelEncryptionKeyBaseView)
    assert issubclass(PaigLevel2EncryptionKeyView, LevelEncryptionKeyBaseView)
