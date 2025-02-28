class GuardrailException(Exception):
    """Custom exception for guardrail provider errors.

    This exception is raised when there are errors related to guardrail operations.
    It includes an optional details attribute for additional context.

    Attributes:
        details (dict): Additional details about the exception, if any.
    """

    def __init__(self, message: str, details: dict = None):
        """
        Initialize a GuardrailException instance.

        Args:
            message (str): Error message to be displayed.
            details (dict, optional): Additional context about the error. Defaults to an empty dictionary.
        """
        super().__init__(message)
        self.details = details if details is not None else {}
