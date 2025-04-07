from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import logging



logger = logging.getLogger(__name__)

# Constants for AES/GCM encryption
CIPHER_ALGO = "AES/GCM/NoPadding"
SECRET_KEY_FACTORY_ALGO = "PBKDF2WithHmacSHA256"
SECRET_KEY_ALGO = "AES"
ITERATION_COUNT = 65536
KEY_LENGTH = 256
# Convert negative values to their unsigned byte equivalents
IV = bytes([163, 124, 145, 182, 239, 45, 67, 143, 153, 116, 205, 86])
SALT = bytes([72, 22, 44, 56, 72, 121, 109, 68])


def apikey_encrypt(data: str, secret: str) -> str:
    """
    Encrypt the given data using AES/GCM encryption.

    Args:
        data: The string to encrypt
        secret: The secret to use for encryption

    Returns:
        Base64 URL-safe encoded encrypted string
    """
    try:
        key = _get_secret_key(secret)
        cipher = _get_cipher(key)

        # Encrypt the data and get the authentication tag
        encrypted_data = cipher.update(data.encode()) + cipher.finalize()

        # Combine IV, encrypted data, and tag
        result = IV + encrypted_data + cipher.tag
        return base64.urlsafe_b64encode(result).decode('utf-8')
    except Exception as e:
        logger.error("Unable to Encrypt text", exc_info=e)
        raise Exception("Unable to Encrypt text")


def _get_cipher(key: bytes):
    """
    Initialize and return the AES/GCM cipher.
    """
    cipher = Cipher(
        algorithms.AES(key),
        modes.GCM(IV),
        backend=default_backend()
    )
    return cipher.encryptor()


def _get_secret_key(secret: str) -> bytes:
    """
    Generate a secret key using PBKDF2 with SHA256.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH // 8,  # Convert bits to bytes
        salt=SALT,
        iterations=ITERATION_COUNT,
        backend=default_backend()
    )
    return kdf.derive(secret.encode())


def apikey_decrypt(encrypted_data: str, password: str, version: str = None) -> str:
    """
    Decrypt the given encrypted data using AES/GCM decryption.

    Args:
        encrypted_data: The base64 URL-safe encoded encrypted string
        password: The password used for encryption

    Returns:
        Decrypted string
    """
    try:
        # Add padding if needed
        padding = 4 - (len(encrypted_data) % 4)
        if padding != 4:
            encrypted_data += '=' * padding

        # Decode the base64 string
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)

        # Extract IV, encrypted data, and tag
        iv = encrypted_bytes[:12]  # First 12 bytes are IV
        tag = encrypted_bytes[-16:]  # Last 16 bytes are tag
        ciphertext = encrypted_bytes[12:-16]  # Middle bytes are encrypted data

        # Create decryptor
        key = _get_secret_key(password)
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=default_backend()
        ).decryptor()

        # Decrypt the data
        decrypted_data = cipher.update(ciphertext) + cipher.finalize()
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logger.error("Unable to Decrypt text", exc_info=e)
        raise Exception("Unable to Decrypt text")


def mask_api_key(api_key: str) -> str:
    """
    Mask an API key by showing only the first 5 and last 5 characters.

    Args:
        api_key: The API key to mask

    Returns:
        Masked API key with format: first 5 chars + 8 asterisks + last 5 chars
    """
    return f"{api_key[:5]}{'*' * 8}{api_key[-5:]}"






