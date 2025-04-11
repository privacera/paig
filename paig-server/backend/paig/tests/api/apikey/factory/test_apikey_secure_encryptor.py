import pytest
import base64
from api.apikey.factory.apikey_secure_encryptor import apikey_encrypt, apikey_decrypt, mask_api_key

SECRET = "test_secret"
DATA = "my_secret_data"


def test_apikey_encrypt_and_decrypt():
    encrypted = apikey_encrypt(DATA, SECRET)
    assert isinstance(encrypted, str)
    # should be base64-url-safe
    base64.urlsafe_b64decode(encrypted + '==')  # will raise error if invalid
    decrypted = apikey_decrypt(encrypted, SECRET)
    assert decrypted == DATA


def test_apikey_encrypt_output_differs_with_different_data():
    enc1 = apikey_encrypt("data1", SECRET)
    enc2 = apikey_encrypt("data2", SECRET)
    assert enc1 != enc2


def test_apikey_encrypt_output_differs_with_different_secret():
    enc1 = apikey_encrypt(DATA, "secret1")
    enc2 = apikey_encrypt(DATA, "secret2")
    assert enc1 != enc2


def test_apikey_decrypt_invalid_base64():
    with pytest.raises(Exception, match="Unable to Decrypt text"):
        apikey_decrypt("invalid$$base64", SECRET)


def test_apikey_decrypt_wrong_password():
    encrypted = apikey_encrypt(DATA, SECRET)
    with pytest.raises(Exception, match="Unable to Decrypt text"):
        apikey_decrypt(encrypted, "wrong_password")


def test_mask_api_key_short_string():
    key = "1234abc56789"
    masked = mask_api_key(key)
    assert masked == "1234a********56789"[:len(key)+8]


def test_mask_api_key_standard_length():
    key = "abcdefghij123456789"
    masked = mask_api_key(key)
    assert masked == "abcde********56789"[:len(key)+8]  # truncated correctly


def test_mask_api_key_edge_case_less_than_10_chars():
    key = "shortkey"
    masked = mask_api_key(key)
    assert masked.startswith(key[:5])  # no error
    assert masked.endswith(key[-5:])


def test_encrypt_invalid_type():
    with pytest.raises(Exception, match="Unable to Encrypt text"):
        apikey_encrypt(12345, SECRET)  # non-string input


def test_decrypt_invalid_type():
    with pytest.raises(Exception, match="Unable to Decrypt text"):
        apikey_decrypt(12345, SECRET)
