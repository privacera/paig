import base64
import secrets


class MasterKeyGenerator:
    """
    Generates a secure master key of the specified length.
    """

    @staticmethod
    def generate_master_key(length: int = 256) -> str:
        """
        Generates a random secure master key of the specified length.

        Args:
            length (int): The length of the master key in bytes. Default is 256 bytes (256 bits).

        Returns:
            str: The generated master key encoded in base64.
        """
        key = secrets.token_bytes(length)
        return base64.b64encode(key).decode()
