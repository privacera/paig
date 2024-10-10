from typing import Any


class ScannerResult:
    """
    A class to represent the result of a scanner operation.

    Attributes:
        traits (list): A list of tags identified by the scanner.
        **kwargs: Additional properties dynamically set from the scanner.
        E.g.
        analyzer_result (list): A list of results from the analyzer.
        score (float): The score assigned by the scanner.
        actions (list): A list of actions recommended by the scanner.
        output_text (str or None): The output text if any intervention occurs.
    """

    def __init__(self, traits: list, **kwargs):
        """
        Initializes a new instance of the ScannerResult class with default values.
        """
        self.traits = traits
        # Dynamically set all properties from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, key, default=None) -> Any | None:
        """
        Retrieve a property by key. Returns default if the key does not exist.
        """
        return getattr(self, key, default)

    def get_traits(self) -> list:
        """
        Retrieve the traits identified by the scanner.
        """
        return self.traits
