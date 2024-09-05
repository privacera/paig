import pytest

import paig_client.encryption


# test the paig_client.encryption.RSAKeyUtil class
def test_RSAKeyUtil(setup_curr_dir):
    rsa_key_util = paig_client.encryption.RSAKeyUtil()
    rsa_key_info = rsa_key_util.generate_key_pair()
    assert rsa_key_info is not None

    data_encryptor = paig_client.encryption.DataEncryptor(
        public_key=rsa_key_info.public_key_encoded_str,
        private_key=rsa_key_info.private_key_encoded_str
    )

    curr_dir = setup_curr_dir
    with open(curr_dir + "/data/prompt-encrypt-fails.txt", "r") as f:
        original_data = f.read()

    encrypted_data = data_encryptor.encrypt(original_data)
    assert original_data != encrypted_data

    decrypted_data = data_encryptor.decrypt(encrypted_data)
    assert original_data == decrypted_data


def test_data_encryptor_non_ascii(setup_curr_dir):
    curr_dir = setup_curr_dir
    with open(curr_dir + "/data/prompt-with-non-ascii-chars.txt", "r") as f:
        original_data = f.read()

    rsa_key_util = paig_client.encryption.RSAKeyUtil()
    rsa_key_info = rsa_key_util.generate_key_pair()

    data_encryptor = paig_client.encryption.DataEncryptor(
        public_key=rsa_key_info.public_key_encoded_str,
        private_key=rsa_key_info.private_key_encoded_str
    )
    encrypted_data = data_encryptor.encrypt(original_data)
    assert original_data != encrypted_data

    decrypted_data = data_encryptor.decrypt(encrypted_data)

    assert decrypted_data == original_data
