from api.shield.model.authorize_request import AuthorizeRequest


class AuthorizeResponse:
    """
    A class to represent an authorization response.
    """

    def __init__(self, is_allowed, response_messages, auth_req: AuthorizeRequest):
        """
        Initializes an instance of AuthorizeResponse.
        """
        self.threadId = auth_req.thread_id
        self.requestId = auth_req.request_id
        self.sequenceNumber = auth_req.sequence_number
        self.isAllowed = is_allowed
        self.responseMessages = response_messages
