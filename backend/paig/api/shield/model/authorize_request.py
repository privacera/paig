from typing import Dict
from api.shield.utils.custom_exceptions import BadRequestException


class AuthorizeRequest:
    """
       A class to represent an authorization request.
    """

    def __init__(self, req_data: Dict, tenant_id: str, user_role: str):
        """
        Initializes an instance of AuthorizeRequest.

        Args:
            req_data (Dict): The request data as a dictionary.
            tenant_id (str): The tenant ID.
            user_role (str): The user role.
        """
        # Mandatory fields
        self.tenant_id = tenant_id
        self.thread_id = self.extract_data(req_data, "threadId")
        self.request_id = self.extract_data(req_data, "requestId")
        self.sequence_number = self.extract_data(req_data, "sequenceNumber")
        self.request_type = self.extract_data(req_data, "requestType")
        self.request_datetime = self.extract_data(req_data, "requestDateTime")
        self.application_key = self.extract_data(req_data, "applicationKey")
        self.client_application_key = self.extract_data(req_data, "clientApplicationKey")
        self.shield_server_key_id = self.extract_data(req_data, "shieldServerKeyId")
        self.shield_plugin_key_id = self.extract_data(req_data, "shieldPluginKeyId")
        self.user_id = str(self.extract_data(req_data, "userId")).lower()

        # Optional fields
        self.messages = req_data.get("messages") if req_data.get("messages") else []
        self.conversation_id = req_data.get("conversationId")
        self.context = req_data.get("context")
        self.client_ip = req_data.get("clientIp")
        self.client_hostname = req_data.get("clientHostName")
        self.stream_id = req_data.get("streamId")
        self.enable_audit = req_data.get("enableAudit")
        self.user_role = user_role

    @staticmethod
    def extract_data(req_data, key):
        """
        Extracts data from the request dictionary.

        Args:
            req_data (Dict): The request data as a dictionary.
            key (str): The key to extract from the request data.

        Returns:
            The extracted data.

        Raises:
            BadRequestException: If the key is missing in the request data.
        """
        data = req_data.get(key)
        if not data:
            raise BadRequestException(f"Missing {key} in request")
        return data
