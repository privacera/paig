import base64

from api.encryption.utils.master_key_generator import MasterKeyGenerator


def test_generate_master_key():
    key_length = 32
    master_key = MasterKeyGenerator.generate_master_key(key_length)

    # Check if the returned value is a string
    assert isinstance(master_key, str)

    # Decode the base64 encoded key and check length
    decoded_key = base64.b64decode(master_key.encode())
    assert len(decoded_key) == key_length


def test_generate_master_key_edge_cases():
    # Test with different key lengths
    for key_length in [16, 64, 128, 256]:
        master_key = MasterKeyGenerator.generate_master_key(key_length)

        # Decode the base64 encoded key and check length
        decoded_key = base64.b64decode(master_key.encode())
        assert len(decoded_key) == key_length

        # Ensure key is non-empty
        assert decoded_key

    # Test with edge cases for very small and large key lengths
    small_key_length = 8
    large_key_length = 512

    small_master_key = MasterKeyGenerator.generate_master_key(small_key_length)
    large_master_key = MasterKeyGenerator.generate_master_key(large_key_length)

    # Decode the base64 encoded keys and check lengths
    decoded_small_key = base64.b64decode(small_master_key.encode())
    decoded_large_key = base64.b64decode(large_master_key.encode())

    assert len(decoded_small_key) == small_key_length
    assert len(decoded_large_key) == large_key_length

    # Ensure keys are non-empty
    assert decoded_small_key
    assert decoded_large_key
