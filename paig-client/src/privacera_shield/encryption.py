import base64
import logging

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

_logger = logging.getLogger(__name__)


class RSAKeyUtil:
    KEY_ALGO_NAME = "RSA"
    DEFAULT_KEY_LENGTH = 1024

    @staticmethod
    def generate_key_pair():

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=RSAKeyUtil.DEFAULT_KEY_LENGTH,
            backend=default_backend()
        )

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_key = private_key.public_key()

        # Serialize the public key to PEM format
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        public_key_str = public_key_pem.decode("utf-8")

        # Remove "BEGIN PUBLIC KEY" and "END PUBLIC KEY" lines
        public_key_str = public_key_str.replace("-----BEGIN PUBLIC KEY-----", "")
        public_key_str = public_key_str.replace("-----END PUBLIC KEY-----", "")
        public_key_str = public_key_str.replace("\n", "")

        private_key_str = private_key_pem.decode("utf-8")

        # Remove "BEGIN PUBLIC KEY" and "END PUBLIC KEY" lines
        private_key_str = private_key_str.replace("-----BEGIN PRIVATE KEY-----", "")
        private_key_str = private_key_str.replace("-----END PRIVATE KEY-----", "")
        private_key_str = private_key_str.replace("\n", "")

        return RSAKeyInfo(private_key_str, public_key_str)

    @staticmethod
    def str_to_private_key(private_key_str):
        try:
            private_key_bytes = base64.b64decode(private_key_str)
            private_key_instance = serialization.load_der_private_key(private_key_bytes, password=None)
            return private_key_instance
        except (ValueError, Exception) as e:
            print(f"Failed to parse private_key_content: {str(e)}")
            return None

    @staticmethod
    def str_to_public_key(public_key_str):
        try:
            public_key_bytes = base64.b64decode(public_key_str)
            public_key_instance = serialization.load_der_public_key(public_key_bytes)
            return public_key_instance
        except (ValueError, Exception) as e:
            print(f"Failed to parse public_key_content: {str(e)}")
            return None


class RSAKeyInfo:
    def __init__(self, private_key_encoded_str, public_key_encoded_str):
        self.private_key_encoded_str = private_key_encoded_str
        self.public_key_encoded_str = public_key_encoded_str

    def __str__(self):
        return f"privateKeyEncodedStr={self.private_key_encoded_str}, publicKeyEncodedStr={self.public_key_encoded_str}"


class DataEncryptor:

    def __init__(self, public_key: str, private_key: str):
        _logger.debug("==> DataEncryptor()")

        # Load public key
        self.public_key = None
        if public_key is not None:
            self.public_key = RSAKeyUtil.str_to_public_key(public_key)

        # Load private key
        self.private_key = None
        if private_key is not None:
            self.private_key = RSAKeyUtil.str_to_private_key(private_key)

        _logger.debug("<== DataEncryptor()")

    def encrypt_data(self, data):
        # first convert to byte array the entire data string using UTF-8 encoding
        # then split into 1024 bit chunks and encrypt each chunk to base64 encoded string
        # join all the base64 encoded strings and return the encrypted data as a string
        data_bytes = data.encode("utf-8")

        # since it is a 1024 bit key, we can encrypt upto 118 bytes at a time so
        # we need to break the data into chunks of 100 bytes (safe side)
        chunk_size = 100
        chunks = [data_bytes[i:i + chunk_size] for i in range(0, len(data_bytes), chunk_size)]

        processed_data_parts = [self.encrypt_chunk(chunk) for chunk in chunks]

        return ''.join(processed_data_parts)

    def decrypt_data(self, data):
        # split the encrypted data string which is base64 encoded into 172 bytes chunks which is 128 bytes of encrypted data
        # decrypt each chunk and get the bytes and join all the bytes to get the original data
        # finally encode the entire byte array to string using UTF-8 encoding

        # the encrypted data will be 128 byte long which is 172 bytes base64 encoded
        chunk_size = 172
        chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

        processed_data_parts_bytes = [self.decrypt_chunk(chunk) for chunk in chunks]

        return (b''.join(processed_data_parts_bytes)).decode("utf-8")

    def encrypt_chunk(self, chunk: bytes) -> str:
        """Encrypts a chunk of data bytes and returns the base64 encoded encrypted data."""
        encrypted_data = self.public_key.encrypt(
            chunk,
            padding.PKCS1v15()
        )
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt_chunk(self, chunk: str) -> bytes:
        """Decrypts a chunk of base64 encoded data and returns the decrypted data bytes."""
        encrypted_data_bytes = base64.b64decode(chunk)
        decrypted_data_bytes = self.private_key.decrypt(
            encrypted_data_bytes,
            padding.PKCS1v15()
        )
        return decrypted_data_bytes

    def encrypt(self, data):
        if self.public_key is None:
            raise ValueError("public key is not set")
        return self.encrypt_data(data)

    def decrypt(self, data):
        if self.private_key is None:
            raise ValueError("private key is not set")
        return self.decrypt_data(data)


class EncryptionKeyInfo:
    def __init__(self, response_dict):
        self.response_dict = response_dict

        self.id = -1
        self.publicKeyValue = None
        self.privateKeyValue = None
        self.keyStatus = None
        self.keyType = None
        self.tenantId = None

        if "id" in response_dict:
            self.id = response_dict["id"]

        if "publicKeyValue" in response_dict:
            self.publicKeyValue = response_dict["publicKeyValue"]

        if "privateKeyValue" in response_dict:
            self.privateKeyValue = response_dict["privateKeyValue"]

        if "keyStatus" in response_dict:
            self.keyStatus = response_dict["keyStatus"]

        if "keyType" in response_dict:
            self.keyType = response_dict["keyType"]

        if "tenantId" in response_dict:
            self.tenantId = response_dict["tenantId"]

    def to_dict(self):
        # Serialize the object to a JSON-formatted string
        return self.response_dict
