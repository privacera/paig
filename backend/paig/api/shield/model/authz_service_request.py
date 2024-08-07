from api.shield.model.authorize_request import AuthorizeRequest
from api.shield.model.request_type import RequestType


class AuthzServiceRequest:
    """
    A class to represent a request for authorization service.
    """

    def __init__(self, auth_req: AuthorizeRequest, traits: list):
        """
        Initializes an instance of AuthzServiceRequest.

        Args:
            auth_req (AuthorizeRequest): The original authorization request.
            traits (list): A list of traits associated with the request.
        """
        self.conversationId = auth_req.conversation_id
        self.threadId = auth_req.thread_id
        self.requestId = auth_req.request_id
        self.sequenceNumber = auth_req.sequence_number
        self.requestDateTime = auth_req.request_datetime

        self.applicationKey = auth_req.application_key
        self.clientApplicationKey = auth_req.client_application_key

        if auth_req.request_type == RequestType.ENRICHED_PROMPT or auth_req.request_type == RequestType.RAG:
            self.requestType = "prompt"
        else:
            self.requestType = auth_req.request_type

        self.traits = traits
        self.userId = auth_req.user_id
        self.enforce = True
        self.context = auth_req.context
        self.user_role = auth_req.user_role

    def to_payload_dict(self):
        """
        Serialize the AuthzServiceRequest instance to a dictionary.

        Returns:
            str: JSON representation of the instance.
        """

        request_dict = {
            "conversationId": self.conversationId,
            "threadId": self.threadId,
            "requestId": self.requestId,
            "sequenceNumber": self.sequenceNumber,
            "requestDateTime": self.requestDateTime,
            "applicationKey": self.applicationKey,
            "clientApplicationKey": self.clientApplicationKey,
            "requestType": self.requestType,
            "traits": self.traits,
            "userId": self.userId,
            "enforce": self.enforce,
            "context": self.context,
        }

        return request_dict
