import pytest

from api.encryption.utils.secure_encryptor import SecureEncryptor

master_key = "supersecretkey"


@pytest.fixture
def encryptor():
    return SecureEncryptor(master_key)


def test_initialization_valid_key(encryptor):
    encryptor = SecureEncryptor(master_key)
    assert encryptor.master_key_in_bytes == encryptor.secret_key


def test_initialization_invalid_key():
    with pytest.raises(ValueError):
        SecureEncryptor(None)


def test_encrypt_decrypt_valid(encryptor):
    plaintext = "Hello, World!"
    encrypted_text = encryptor.encrypt(plaintext)
    decrypted_text = encryptor.decrypt(encrypted_text)
    assert decrypted_text == plaintext


def test_encrypt_decrypt_none_input(encryptor):
    assert encryptor.encrypt(None) is None
    assert encryptor.decrypt(None) is None


def test_encrypt_starts_with_prefix(encryptor):
    plaintext = "Hello, World!"
    encrypted_text = encryptor.encrypt(plaintext)
    assert encrypted_text.startswith(encryptor.PREFIX_ENCRYPT_TEXT)


def test_decrypt_invalid_prefix(encryptor):
    invalid_encrypted_text = "InvalidPrefix:" + encryptor.encrypt("Hello")
    decrypted_text = encryptor.decrypt(invalid_encrypted_text)
    assert decrypted_text == invalid_encrypted_text  # should return the original text if prefix is invalid


def test_encrypt_decrypt_with_timestamp(encryptor):
    encryptor.TIMESTAMP_ON_CRYPT = True
    plaintext = "Hello, World!"
    encrypted_text = encryptor.encrypt(plaintext)
    decrypted_text = encryptor.decrypt(encrypted_text)
    assert decrypted_text == plaintext


def test_encrypt_invalid(encryptor):
    with pytest.raises(RuntimeError):
        encryptor.secret_key = 'abcd'
        plaintext = "Hello, World!"
        encrypted_text = encryptor.encrypt(plaintext)
        decrypted_text = encryptor.decrypt(encrypted_text)
        assert decrypted_text == plaintext


def test_decrypt_invalid(encryptor):
    with pytest.raises(RuntimeError):
        plaintext = "Hello, World!"
        encrypted_text = encryptor.encrypt(plaintext)
        decryptor = SecureEncryptor(encrypted_text)
        decrypted_text = decryptor.decrypt(encrypted_text)
        assert decrypted_text == plaintext
