from abc import ABC


class Scanner(ABC):
    """
    Scanner class that holds the properties of a scanner.
    """

    def __init__(self, **kwargs):
        """
        Initialize the required models and variables for the scanner.
        All properties are dynamically set via kwargs.
        """
        # Dynamically set all properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_property(self, key):
        """
        Retrieve a property by key. Returns None if the key does not exist.
        """
        return getattr(self, key, None)

    def scan(self, message: str) -> dict:
        """
        Process and sanitize the input prompt according to the specific scanner's implementation.

        Parameters:
            message (str): The input prompt that needs to be processed.

        Returns:
            dict: dictionary consisting of tags and other additional infos
            e.g. {'tags': ['PII', 'PHI']}
            e.g. {'tags': ['TOXIC'], 'analyzerResult': [{'score': 0.99}, {'reason': 'Profanity'}]}
        """
