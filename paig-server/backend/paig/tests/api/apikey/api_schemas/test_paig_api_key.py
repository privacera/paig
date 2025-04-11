import pytest
from datetime import datetime
from api.apikey.api_schemas.paig_api_key import (
    PaigApiKeyView,
    GenerateApiKeyRequest,
    GenerateApiKeyResponse
)

def test_paig_api_key_view_instantiation():
    data = {
        "tenantId": 1,
        "apiKeyName": "Test Key",
        "userId": 10,
        "addedById": 100,
        "updatedById": 101,
        "key_status": "ACTIVE",
        "description": "This is a test key",
        "lastUsedOn": "2024-01-01T12:00:00",
        "apiKeyMasked": "xyz****abcd",
        "apiKeyEncrypted": "encrypted_key_value",
        "tokenExpiry": "2025-01-01T00:00:00",
        "neverExpire": False,
        "apiScopeId": "3",
        "version": "v1",
        "applicationId": 22
    }

    view = PaigApiKeyView(**data)

    assert view.api_key_name == "Test Key"
    assert view.api_key_masked == "xyz****abcd"
    assert view.expiry == "2025-01-01T00:00:00"
    assert view.tenant_id == 1
    assert view.application_id == 22

def test_generate_api_key_request_validation_success():
    data = {
        "apiKeyName": "New Key",
        "description": "Used for testing",
        "neverExpire": True,
        "tokenExpiry": "2025-12-31T23:59:59",
        "applicationId": 5
    }

    model = GenerateApiKeyRequest(**data)

    assert model.api_key_name == "New Key"
    assert model.application_id == 5

def test_generate_api_key_request_missing_application_id_raises():
    data = {
        "apiKeyName": "Test Key",
        "description": "Missing api key name",
        "neverExpire": False,
        "tokenExpiry": "2025-01-01T00:00:00"
    }

    with pytest.raises(Exception) as exc_info:
        GenerateApiKeyRequest(**data)
    assert "Field required" in str(exc_info.value)

def test_generate_api_key_response_instantiation():
    now = datetime.now()
    data = {
        "id": 99,
        "apiKeyName": "Key Res",
        "description": "Response test",
        "neverExpire": False,
        "tokenExpiry": now.isoformat(),
        "applicationId": 3,
        "userId": 12,
        "addedById": 13,
        "updatedById": 14,
        "status": 1,
        "createTime": now.isoformat(),
        "updateTime": now.isoformat(),
        "keyStatus": "ACTIVE",
        "tenantId": "tenant_456",
        "apiKeyMasked": "abcd****1234",
        "apiScopeId": [4, 5],
        "version": "v2"
    }

    model = GenerateApiKeyResponse(**data)

    assert model.id == 99
    assert model.api_key_name == "Key Res"
    assert model.user_id == 12
    assert model.status == 1
    assert model.key_status == "ACTIVE"
    assert model.api_scope_id == [4, 5]

