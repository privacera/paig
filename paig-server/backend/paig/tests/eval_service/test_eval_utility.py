import pytest

from services.eval.paig_eval_service.utility import encrypt_target_creds, decrypt_target_creds, locate_auth_header


@pytest.mark.asyncio
async def test_encrypt_and_decrypt_roundtrip():
    original_token = "my-secret-token"
    headers = {"Authorization": original_token}

    # Encrypt the header
    encrypted_headers = await encrypt_target_creds(headers.copy())

    assert encrypted_headers["Authorization"] != original_token  # Ensure encryption happened

    # Decrypt the header
    decrypted_headers = await decrypt_target_creds(encrypted_headers.copy())

    assert decrypted_headers["Authorization"] == original_token  # Should return to original


@pytest.mark.asyncio
async def test_encrypt_target_creds_with_no_auth():
    headers = {"Content-Type": "application/json"}

    result = await encrypt_target_creds(headers.copy())

    assert result == headers  # Should remain unchanged


@pytest.mark.asyncio
async def test_decrypt_target_creds_with_no_auth():
    headers = {"X-Api-Key": "value"}

    result = await decrypt_target_creds(headers.copy())

    assert result == headers  # Should remain unchanged


def test_locate_auth_header_found():
    headers = {"Authorization": "secret"}
    key, value = locate_auth_header(headers)

    assert key == "Authorization"
    assert value == "secret"


def test_locate_auth_header_case_insensitive():
    headers = {"authorization": "token"}
    key, value = locate_auth_header(headers)

    assert key == "authorization"
    assert value == "token"


def test_locate_auth_header_not_found():
    headers = {"Content-Type": "application/json"}
    key, value = locate_auth_header(headers)

    assert key is None
    assert value is None
