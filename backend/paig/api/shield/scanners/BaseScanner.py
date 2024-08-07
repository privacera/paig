from abc import ABC


class Scanner(ABC):
    """
    Scanner class that holds the properties of a scanner.
    """

    def __init__(self, name, request_types, enforce_access_control, model_path, model_score_threshold, entity_type,
                 enable, **kwargs):
        """
        Initialize the required models and variables for the scanner

        """
        self.name = name
        self.request_types = request_types
        self.enforce_access_control = enforce_access_control
        self.model_path = model_path
        self.model_score_threshold = model_score_threshold
        self.entity_type = entity_type
        self.enable = enable

        # Handle additional properties
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_property(self, key):
        return getattr(self, key, None)

    def scan(self, message: str) -> dict:
        """
        Process and sanitize the input prompt according to the specific scanner's implementation.

        Parameters:
            message (str): The input prompt that needs to be processed.

        Returns:
            dict: dictionary consisting of tags and other additional infos
        """
