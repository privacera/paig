from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def generate_key_pair():
    key_size = 2048  # Should be at least 2048

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
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
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
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return message_decrypted
    except ValueError:
        return "Failed to Decrypt"


# message_decrypted = decrypt(message_encrypted, private_key)
# print(message_decrypted.decode("utf-8"))

with open("./bad-prompt.txt", "r") as f:
    original_data = f.read()

for i in range(1, len(original_data)):
    input_data = original_data[:i]
    original_bytes = input_data.encode("utf-8")
    # print(f"Original Text: {original_data}\nOriginal bytes: len={len(original_bytes)}")
    print(f"input data len= {len(original_bytes)}")
    message_encrypted = encrypt(original_bytes, public_key)
    print(f"input data len= {len(original_bytes)}, Encrypted Text: {message_encrypted.hex()}, len={len(message_encrypted)}")
