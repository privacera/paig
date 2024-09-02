import base64
import logging
from datetime import datetime
from typing import Union
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7


class SecureEncryptor:
    """
    SecureEncryptor provides encryption and decryption functionality using AES algorithm.

    Attributes:
        CIPHER_ALGO: The cipher algorithm to use (AES).
        KEY_ALGO: The key algorithm name.
        PREFIX_ENCRYPT_TEXT: The prefix added to the encrypted text.
        PREFIX_ENCRYPT_TEXT_LEN: The length of the prefix.
        TIMESTAMP_ON_CRYPT: Flag to include timestamp in encryption.
        KEY_SIZE_IN_BYTES: The key size in bytes.
    """
    CIPHER_ALGO = algorithms.AES
    KEY_ALGO = 'AES'
    PREFIX_ENCRYPT_TEXT = "PrivaceraEncrypt:"
    PREFIX_ENCRYPT_TEXT_LEN = len(PREFIX_ENCRYPT_TEXT)
    TIMESTAMP_ON_CRYPT = True
    KEY_SIZE_IN_BYTES = 16

    def __init__(self, master_key: str):
        """
        Initializes the SecureEncryptor with the provided master key.

        Args:
            master_key (str): The master key for encryption and decryption.

        Raises:
            ValueError: If the master key is None or empty.
        """
        if not master_key:
            raise ValueError("Unable to create SecureEncryptor due to null master key")

        self.master_key_in_bytes = self.make_fixed_length_key(master_key.encode(), self.KEY_SIZE_IN_BYTES)
        self.secret_key = self.master_key_in_bytes
        self.backend = default_backend()
        self.logger = logging.getLogger(self.__class__.__name__)

    # noinspection PyMethodMayBeStatic
    def make_fixed_length_key(self, key: bytes, length: int) -> bytes:
        """
        Adjusts the key to a fixed length by repeating or truncating it.

        Args:
            key (bytes): The original key.
            length (int): The desired length of the key.

        Returns:
            bytes: The adjusted key of the desired length.
        """
        if len(key) < length:
            key += key * (length // len(key)) + key[:length % len(key)]
        return key[:length]

    def encrypt(self, text: str) -> Union[str, None]:
        """
        Encrypts the provided text.

        Args:
            text (str): The text to encrypt.

        Returns:
            Union[str, None]: The encrypted text with a prefix, or None if the input is None.

        Raises:
            RuntimeError: If encryption fails.
        """
        if text is None:
            return None

        try:
            cipher = Cipher(self.CIPHER_ALGO(self.secret_key), modes.ECB(), backend=self.backend)
            encryptor = cipher.encryptor()
            padder = PKCS7(128).padder()

            text_to_encrypt = (f"{datetime.now().timestamp()}:{text}" if self.TIMESTAMP_ON_CRYPT else text).encode()
            padded_data = padder.update(text_to_encrypt) + padder.finalize()
            encrypted_bytes = encryptor.update(padded_data) + encryptor.finalize()

            encoded_encrypted_bytes = base64.b64encode(encrypted_bytes).decode()
            return self.PREFIX_ENCRYPT_TEXT + encoded_encrypted_bytes

        except Exception as e:
            self.logger.error("Unable to Encrypt text", exc_info=e)
            raise RuntimeError("Unable to Encrypt text") from e

    def decrypt(self, encrypted_text: str) -> Union[str, None]:
        """
        Decrypts the provided encrypted text.

        Args:
            encrypted_text (str): The encrypted text to decrypt.

        Returns: Union[str, None]: The decrypted text, or the original text if it's not prefixed correctly,
        or None if the input is None.

        Raises:
            RuntimeError: If decryption fails.
        """
        if encrypted_text is None:
            return encrypted_text

        if not encrypted_text.startswith(self.PREFIX_ENCRYPT_TEXT):
            return encrypted_text

        try:
            encoded_encrypted_bytes = encrypted_text[self.PREFIX_ENCRYPT_TEXT_LEN:].encode()
            encrypted_bytes = base64.b64decode(encoded_encrypted_bytes)

            cipher = Cipher(self.CIPHER_ALGO(self.secret_key), modes.ECB(), backend=self.backend)
            decryptor = cipher.decryptor()
            decrypted_padded_bytes = decryptor.update(encrypted_bytes) + decryptor.finalize()

            unpadder = PKCS7(128).unpadder()
            decrypted_bytes = unpadder.update(decrypted_padded_bytes) + unpadder.finalize()
            decrypted_text = decrypted_bytes.decode()

            if self.TIMESTAMP_ON_CRYPT:
                delimiter_index = decrypted_text.find(':')
                if delimiter_index != -1:
                    return decrypted_text[delimiter_index + 1:]
            return decrypted_text

        except Exception as e:
            self.logger.error("Unable to Decrypt text", exc_info=e)
            raise RuntimeError("Unable to Decrypt text") from e
