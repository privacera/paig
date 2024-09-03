import logging

from .encryption import DataEncryptor

logger = logging.getLogger(__name__)


class PluginAccessRequestEncryptor:

    def __init__(self, tenant_id, encryption_keys_info: dict):
        self.tenant_id = tenant_id

        # Create shield data encryptor
        self.shield_data_encryptor = DataEncryptor(
            public_key=encryption_keys_info["shield_server_public_key"],
            private_key=None
        )

        # Create plugin's public and private key and data encryptor
        self.plugin_data_encryptor = DataEncryptor(
            public_key=None,
            private_key=encryption_keys_info["shield_plugin_private_key"],
        )

        self.shield_server_key_id = encryption_keys_info["shield_server_key_id"]
        self.shield_plugin_key_id = encryption_keys_info["shield_plugin_key_id"]

    def encrypt_message(self, message):
        return self.shield_data_encryptor.encrypt(message)

    def encrypt_request(self, request):
        messages = request.request_text
        encrypted_messages = []
        for message in messages:
            encrypted_message = self.shield_data_encryptor.encrypt(message)
            encrypted_messages.append(encrypted_message)

        request.request_text = encrypted_messages

    def decrypt_response(self, response):
        messages = response.responseMessages
        decrypted_messages = []
        for message in messages:
            decrypted_message = message.copy()
            decrypted_message["responseText"] = self.plugin_data_encryptor.decrypt(message["responseText"])
            decrypted_messages.append(decrypted_message)

        response.responseMessages = decrypted_messages
