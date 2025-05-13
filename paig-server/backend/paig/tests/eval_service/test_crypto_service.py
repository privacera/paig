import pytest
from services.eval.paig_eval_service.factory.crypto_service import CryptoService
from api.encryption.events.startup import create_encryption_master_key_if_not_exists


@pytest.mark.asyncio
async def test_crypto_service_encrypt_decrypt_roundtrip(db_session, set_context_session):
    await create_encryption_master_key_if_not_exists()
    crypto_service = CryptoService()
    original_data = "test-value"

    encrypted = await crypto_service.encrypt(original_data)
    assert isinstance(encrypted, str)
    assert encrypted != original_data  # Ensure it's actually encrypted

    decrypted = await crypto_service.decrypt(encrypted)
    assert decrypted == original_data  # Ensure correct decryption


@pytest.mark.asyncio
async def test_crypto_service_encrypt_multiple_values(db_session, set_context_session):
    await create_encryption_master_key_if_not_exists()
    crypto_service = CryptoService()
    values = ["test1", "12345", "data@!#"]

    for value in values:
        encrypted = await crypto_service.encrypt(value)
        decrypted = await crypto_service.decrypt(encrypted)

        assert decrypted == value
        assert encrypted != value

