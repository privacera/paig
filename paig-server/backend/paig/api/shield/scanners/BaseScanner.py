from abc import ABC, abstractmethod
from typing import Any

from api.shield.model.scanner_result import ScannerResult


class Scanner(ABC):
    """
    Scanner class that holds the properties of a scanner.
    """

    def __init__(self, **kwargs):
        """
        Initialize the required models and variables for the scanner.
        All properties are dynamically set via kwargs.

        Parameters:
        **kwargs: keyword arguments passed from properties file.
        E.g.
        name (str): The name of the scanner.
        request_types (list): List of request types that the scanner will handle.
        enforce_access_control (bool): Flag to enforce access control.
        model_path (str): Path to the model used by the scanner.
        model_score_threshold (float): Threshold score for the model to consider a match.
        entity_type (str): Type of entity the scanner is looking for.
        enable (bool): Flag to ena
        """
        # Dynamically set all properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_property(self, key) -> Any | None:
        """
        Retrieve a property by key. Returns None if the key does not exist.
        """
        return getattr(self, key, None)

    @abstractmethod
    def scan(self, message: str) -> ScannerResult:
        """
        Process and sanitize the input prompt according to the specific scanner's implementation.

        Parameters:
            message (str): The input prompt that needs to be processed.

        Returns:
            ScannerResult: The result of the scanner operation.
        """
