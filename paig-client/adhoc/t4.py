import base64

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def generate_key_pair():
    key_size = 1024  # Should be at least 2048

    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Do not change
        key_size=key_size,
    )

    public_key = private_key.public_key()
    return private_key, public_key


private_key, public_key = generate_key_pair()


def encrypt(message, public_key):
    return public_key.encrypt(
        message,
        padding.PKCS1v15()
    )


#message = b"Hello World!"
# message = "Hello World!".encode("utf-8")
#
# message_encrypted = encrypt(message, public_key)
#
# print(f"Encrypted Text: {message_encrypted.hex()}")


def decrypt(message_encrypted, private_key):
    try:
        message_decrypted = private_key.decrypt(
            message_encrypted,
            padding.PKCS1v15()
        )
        return message_decrypted
    except ValueError:
        return "Failed to Decrypt"


# message_decrypted = decrypt(message_encrypted, private_key)
# print(message_decrypted.decode("utf-8"))

with open("/Users/paresh/gitlab2/privacera/paig/plugin-test/data.txt", "r") as f:
    original_data = f.read()

# for i in range(1, len(original_data)):
#     input_data = original_data[:i]
#     original_bytes = input_data.encode("utf-8")
#     # print(f"Original Text: {original_data}\nOriginal bytes: len={len(original_bytes)}")
#     print(f"input data len= {len(original_bytes)}")
#     message_encrypted = encrypt(original_bytes, public_key)
#     print(f"input data len= {len(original_bytes)}, Encrypted Text: {message_encrypted.hex()}, len={len(message_encrypted)}")
#     encrypted_base64_len = len(base64.b64encode(message_encrypted).decode("utf-8"))
#     print(f"input data len= {len(original_bytes)}, Encrypted Text: {message_encrypted.hex()}, len={len(message_encrypted)}, base64 len={encrypted_base64_len}")

data_bytes = original_data.encode("utf-8")
chunk_size = 100
chunks = [data_bytes[i:i + chunk_size] for i in range(0, len(data_bytes), chunk_size)]

print(f"input data len= {len(data_bytes)}")
print(f"num chunks= {len(chunks)}")
i = 0
processed_data_parts = []
for chunk in chunks:
    # print(f"i={i}, chunk len= {len(chunk)}")
    i += 1
    message_encrypted = encrypt(chunk, public_key)
    processed_data_parts.extend(message_encrypted)
final_encrypted = base64.b64encode(bytes(processed_data_parts))
print(f"final_encrypted len= {len(final_encrypted)}")
print(f"final_encrypted= {final_encrypted.decode('utf-8')}")

decrypt_bytes = base64.b64decode(final_encrypted)
processed_data_parts = []
chunk_size = 128
chunks = [decrypt_bytes[i:i + chunk_size] for i in range(0, len(decrypt_bytes), chunk_size)]
i = 0
for chunk in chunks:
    decrypt_bytes = decrypt(chunk, private_key)
    print(f"i={i}, chunk len= {len(chunk)}, decrypted len= {len(decrypt_bytes)}")
    processed_data_parts.extend(decrypt_bytes)
    i += 1
final_decrypted = bytes(processed_data_parts).decode("utf-8")
print(f"final_decrypted len= {len(final_decrypted)}")
print(f"final_decrypted= {final_decrypted}")
