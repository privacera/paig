import uuid
from typing import Dict
from api.shield.utils.custom_exceptions import BadRequestException

from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.authz_service_response import AuthzServiceResponse


class AccessResultType:
    """Constants representing access result types."""
    ALLOWED = "allowed"
    DENIED = "denied"
    MASKED = "masked"


class BaseAudit:
    """
    A base class for auditing information.
    """
    def __init__(self):
        """Initializes an instance of BaseAudit."""
        self.eventId = str(uuid.uuid4())
        self.eventTime = None
        self.tenantId = None
        self.threadId = None
        self.threadSequenceNumber = None
        self.requestType = None
        self.encryptionKeyId = None
        self.messages = []
        self.conversationId = None
        self.requestId = None
        self.userId = None
        self.clientApplicationKey = None
        self.clientApplicationName = ""
        self.applicationKey = None
        self.applicationName = ""
        self.result = None
        self.traits = None
        self.maskedTraits = {}
        self.context = None
        self.rangerAuditIds = []
        self.rangerPolicyIds = []
        self.paigPolicyIds = []
        self.clientIp = None
        self.clientHostname = None
        self.numberOfTokens = 0

    @staticmethod
    def check_result(authz_res):
        if authz_res.authorized:
            if authz_res.masked_traits:
                return AccessResultType.MASKED
            else:
                return AccessResultType.ALLOWED
        else:
            return AccessResultType.DENIED

    @staticmethod
    def extract_data(req_data, key):
        """
        Determine the result based on the authorization response.

        Args:
            authz_res (AuthzServiceResponse): The authorization service response.

        Returns:
            str: The access result type.
        """
        data = req_data.get(key)
        if not data:
            raise BadRequestException(f"Missing {key} in request")
        return data

    def to_payload_dict(self):
        """
        Extract data from the request dictionary.

        Args:
            req_data (dict): The request data.
            key (str): The key to extract.

        Returns:
            The value associated with the key.

        Raises:
            BadRequestException: If the key is missing in the request data.
        """
        return {
            "eventId": self.eventId,
            "eventTime": self.eventTime,
            "tenantId": self.tenantId,
            "threadId": self.threadId,
            "threadSequenceNumber": self.threadSequenceNumber,
            "requestType": self.requestType,
            "encryptionKeyId": self.encryptionKeyId,
            "messages": self.messages,
            "conversationId": self.conversationId,
            "requestId": self.requestId,
            "userId": self.userId,
            "clientApplicationKey": self.clientApplicationKey,
            "clientApplicationName": self.clientApplicationName,
            "applicationKey": self.applicationKey,
            "applicationName": self.applicationName,
            "result": self.result,
            "traits": self.traits,
            "maskedTraits": self.maskedTraits,
            "context": self.context,
            "rangerAuditIds": self.rangerAuditIds,
            "rangerPolicyIds": self.rangerPolicyIds,
            "paigPolicyIds": self.paigPolicyIds,
            "clientIp": self.clientIp,
            "clientHostname": self.clientHostname,
            "numberOfTokens": self.numberOfTokens
        }

    @classmethod
    def from_payload_dict(cls, payload):
        """
        Create a BaseAudit instance from a dictionary.

        Args:
            payload (dict): The dictionary containing audit information.

        Returns:
            BaseAudit: The created instance.
        """
        instance = cls()
        instance.eventId = payload.get("eventId", str(uuid.uuid4()))
        instance.eventTime = payload.get("eventTime")
        instance.tenantId = payload.get("tenantId")
        instance.threadId = payload.get("threadId")
        instance.threadSequenceNumber = payload.get("threadSequenceNumber")
        instance.requestType = payload.get("requestType")
        instance.encryptionKeyId = payload.get("encryptionKeyId")
        instance.messages = payload.get("messages", [])
        instance.conversationId = payload.get("conversationId")
        instance.requestId = payload.get("requestId")
        instance.userId = payload.get("userId")
        instance.clientApplicationKey = payload.get("clientApplicationKey")
        instance.clientApplicationName = payload.get("clientApplicationName", "")
        instance.applicationKey = payload.get("applicationKey")
        instance.applicationName = payload.get("applicationName", "")
        instance.result = payload.get("result")
        instance.traits = payload.get("traits")
        instance.maskedTraits = payload.get("maskedTraits")
        instance.context = payload.get("context")
        instance.rangerAuditIds = payload.get("rangerAuditIds", [])
        instance.rangerPolicyIds = payload.get("rangerPolicyIds", [])
        instance.paigPolicyIds = payload.get("paigPolicyIds", [])
        instance.clientIp = payload.get("clientIp")
        instance.clientHostname = payload.get("clientHostname")
        instance.numberOfTokens = payload.get("numberOfTokens", 0)
        return instance


class ShieldAudit(BaseAudit):
    """
    A class for Shield audit logs.

    Attributes:
        Inherits all attributes from BaseAudit.
    """
    def __init__(self, auth_req: AuthorizeRequest = None, authz_res: AuthzServiceResponse = None, traits=None,
                 original_masked_txt_map_list=None):
        """
        Initializes an instance of ShieldAudit.

        Args:
            auth_req (AuthorizeRequest, optional): The authorization request.
            authz_res (AuthzServiceResponse, optional): The authorization service response.
            traits (list, optional): List of traits.
            original_masked_txt_map_list (list, optional): List of original masked text maps.
        """
        super().__init__()
        if auth_req and authz_res:
            self.eventTime = auth_req.request_datetime
            self.tenantId = auth_req.tenant_id
            self.threadId = auth_req.thread_id
            self.threadSequenceNumber = auth_req.sequence_number
            self.requestType = auth_req.request_type
            self.encryptionKeyId = auth_req.shield_server_key_id

            self.messages = original_masked_txt_map_list

            # Additional logic specific to ShieldAudit
            self.conversationId = auth_req.conversation_id
            self.requestId = auth_req.request_id
            self.userId = authz_res.user_id if authz_res.user_id else auth_req.user_id
            self.clientApplicationKey = auth_req.client_application_key
            self.clientApplicationName = ""  # get the value from authz_governance service
            self.applicationKey = auth_req.application_key
            self.applicationName = authz_res.application_name if authz_res.application_name else ""
            self.result = self.check_result(authz_res)
            self.traits = traits
            self.maskedTraits = authz_res.masked_traits if authz_res.masked_traits else {}
            self.context = auth_req.context

            # Additional logic for ShieldAudit
            self.rangerAuditIds = authz_res.ranger_audit_ids if authz_res.ranger_audit_ids else []
            self.rangerPolicyIds = authz_res.ranger_policy_ids if authz_res.ranger_policy_ids else []
            self.paigPolicyIds = authz_res.paig_policy_ids if authz_res.paig_policy_ids else []
            self.clientIp = auth_req.client_ip
            self.clientHostname = auth_req.client_hostname


# Using this Object to Audit the Logs while using /shield/audit API
class ShieldAuditViaApi(BaseAudit):
    """
    A class for auditing logs via Shield API.

    Attributes:
        Inherits all attributes from BaseAudit.
    """
    def __init__(self, req_data: Dict):
        """
        Initializes an instance of ShieldAuditViaApi.

        Args:
            req_data (Dict): The request data.
        """
        super().__init__()
        self.eventTime = self.extract_data(req_data, "eventTime")
        self.tenantId = self.extract_data(req_data, "tenantId")
        self.threadId = self.extract_data(req_data, "threadId")
        self.threadSequenceNumber = self.extract_data(req_data, "threadSequenceNumber")
        self.requestType = self.extract_data(req_data, "requestType")
        self.encryptionKeyId = self.extract_data(req_data, "encryptionKeyId")
        self.messages = req_data.get("messages", [])
        self.conversationId = req_data.get("conversationId", "")
        self.requestId = self.extract_data(req_data, "requestId")
        self.userId = self.extract_data(req_data, "userId")
        self.clientApplicationKey = req_data.get("clientApplicationKey", "")
        self.clientApplicationName = req_data.get("clientApplicationName", "")
        self.applicationKey = self.extract_data(req_data, "applicationKey")
        self.applicationName = req_data.get("applicationName", "")
        self.result = self.extract_data(req_data, "result")
        self.traits = req_data.get("traits", [])
        self.maskedTraits = req_data.get("maskedTraits", {})
        self.context = req_data.get("context", {})
        self.rangerAuditIds = req_data.get("rangerAuditIds", [])
        self.rangerPolicyIds = req_data.get("rangerPolicyIds", [])
        self.paigPolicyIds = req_data.get("paigPolicyIds", [])
        self.clientIp = self.extract_data(req_data, "clientIp")
        self.clientHostname = req_data.get("clientHostname", "")
