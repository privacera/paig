import base64
import pytest

from cryptography.hazmat.primitives.asymmetric import padding

from paig_common.encryption import DataEncryptor, RSAKeyUtil

rsa_key_info = RSAKeyUtil().generate_key_pair()
data_encryptor = DataEncryptor(public_key=rsa_key_info.public_key_encoded_str,
                               private_key=rsa_key_info.private_key_encoded_str)

public_key_local = RSAKeyUtil.str_to_public_key(rsa_key_info.public_key_encoded_str)
private_key_local = RSAKeyUtil.str_to_private_key(rsa_key_info.private_key_encoded_str)

msg_data = "Hello, World!"


def test_encrypt_decrypt():
    encrypted_data = data_encryptor.encrypt(msg_data)
    decrypted_data = data_encryptor.decrypt(encrypted_data)
    assert decrypted_data == msg_data


def test_encrypt_decrypt_error():
    # below line contain non-ascii characters “ ” . It should raise UnicodeDecodeError
    non_ascii_char_data = "IndiaandotherSouthAsianCountries to transition to a “high-performing, low-emission, energy secure” economy"
    encrypted_data = data_encryptor.encrypt(non_ascii_char_data)
    with pytest.raises(UnicodeDecodeError):
        print("found issue with old decrypt code! This is expected!")
        decrypt_data(encrypted_data)

    decrypted_data = data_encryptor.decrypt(encrypted_data)
    assert decrypted_data == non_ascii_char_data


# following code is from encryption.py. to simulate the old behavior of decrypt .
def decrypt_chunk(chunk: str) -> str:
    encrypted_data_bytes = base64.b64decode(chunk)
    decrypted_data = private_key_local.decrypt(
        encrypted_data_bytes,
        padding.PKCS1v15()
    )
    return decrypted_data.decode("utf-8")


def decrypt_data(data):
    # the encrypted data will be 128 byte long which is 172 bytes base64 encoded
    chunk_size = 172
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    processed_data_parts = [decrypt_chunk(chunk) for chunk in chunks]
    return ''.join(processed_data_parts)


def test_init_data_encryptor_with_none_keys():
    data_encryptor_local = DataEncryptor(public_key=None, private_key=None)

    with pytest.raises(ValueError):
        data_encryptor_local.encrypt(msg_data)

    with pytest.raises(ValueError):
        data_encryptor_local.decrypt(msg_data)


def test_rsa_util_error_keys():
    public_key_err = RSAKeyUtil.str_to_public_key("MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwn0+nJ2WQfR5zKsPJv7ghGsYYy+En5hDO86IdH5oyY9Y7fN3iQSGCvFPVIiGbpg309Yzxj/9e8pK0QzuinklKS97VBoo+fJUQJt+UUgpfGFQ0Ce3pThDm2KtmZDS3ApB18u1Y4PutZlyiZxqCxftIr9nN8u5CHAGro3ivIOrS2QIDA")
    private_key_err = RSAKeyUtil.str_to_private_key("MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALCfT6cnZZB9HnMqw8m/uCEaxhjL4SfmEM7zoh0fmjJj1jt83eJBIYK8U9UiIZumDfT1jPGP/17ykrRDO6KeSUpL3tUGij58lRAm35RSCl8YVDQJ7elOEObYq2ZkNLcCkHXy7Vjg+61mXKJnGoLF+0iv2c3y7kIcAaujeK8g6tLZAgMBAAECgYAfvNji2AT7pEgS+NXKzI0pQbbkIMq6UTCnB4eThSi/skn+UY9Lh1metPm5fFMetYWfhXpItA/2/07WXph6Pcg8aZp+vWjhE5vumAaZB6hsQ7xaToeNPfHNhHxY0DixHcHE/pwpk3zSlOyhYlFD+cGkOGBEbUthE7NDdSZEN/mR6QJBANlV8rMGN7lpli8+DvtyMSMTEndnijGStiSHzuVjXI+x8TfPTU0EKvbPr1iE5Eb8PJ87MTQBIoaHpUkzO5c8jQ0CQQDQCyohLaZi5CCR4Y92c+wAOALTg6uK/L1zyTg0V7LvaO5ZP6BwH2ta8vMDvqTEXwheealf1jE+lOaSwM7Bx+H9AkA5pjrCkhul6wQTc/q1aAzwqNZ1JdnaXHhEKGIRJtIeq6y4iRyQGVLsNRrl+Bo1WiMaebELgmGOHd0SFazw6PbhAkEAlSrMJEnk+Rb0u2RtRtNLLcT7Uckg4GDjPffS0sTmyX4FF/zk/j+o6+cyk0bIQPyatZKp/MtJN8Pvpt2T4aF9yQJADTPbNSwjEOp6wwH5GevMIloJlc32z5kM1IPaxaHv9GVUecW2MNcpRaI9RqDrKfTSMFbvhJYezQgVuV3j77UU")

    assert public_key_err is None
    assert private_key_err is None
