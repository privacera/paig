from .message import ErrorMessage


class PAIGException(Exception):
    """
    Base class for all PAIG exceptions.
    """

    def __init__(self, error_message: ErrorMessage, **kwargs):
        """
        Initialize a PAIGException instance.

        Args:
            message (str): The error message.
        """
        super().__init__(error_message.format(**kwargs))


class AccessControlException(PAIGException):
    """
    Custom exception for access control violations.
    """
    def __init__(self, server_error_message: str):
        super().__init__(ErrorMessage.PAIG_ACCESS_DENIED, server_error_message=server_error_message)
