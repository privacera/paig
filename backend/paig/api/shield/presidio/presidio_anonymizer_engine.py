from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer import RecognizerResult
from typing import List


class PresidioAnonymizerEngine:
    """
       A class for handling text anonymization using the Presidio Anonymizer.

       This class provides methods to mask sensitive information in text based on the provided
       entities and custom masking values, and to perform anonymization based on analyzer results.

       Attributes:
           anonymizer (AnonymizerEngine): An instance of the Presidio AnonymizerEngine used for anonymization tasks.
       """
    def __init__(self):
        """
        Initializes the PresidioAnonymizerEngine instance and its underlying AnonymizerEngine.
        """
        self.anonymizer = AnonymizerEngine()

    def mask(self, text: str, entities_with_custom_masked_value: dict, analyzer_result: List[RecognizerResult]):
        """
        Masks specified entities in the given text using custom masking values.

        Returns:
            str: The text with specified entities masked according to the provided custom values.
        """
        return self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_result,
            operators=self.__custom_masked_operators(entities_with_custom_masked_value)
        ).text

    @staticmethod
    def __custom_masked_operators(entities_with_custom_masked_value: dict):
        """
        Creates a dictionary of custom operators for masking entities based on provided values.

        Returns:
            dict: A dictionary where keys are entity types and values are OperatorConfig instances for masking.
        """
        operator = {}
        for key, value in entities_with_custom_masked_value.items():
            operator[key] = OperatorConfig("replace", {"new_value": value})
        return operator

    def anonymize(
            self,
            text: str,
            analyzer_result: List[RecognizerResult]
    ) -> str:
        """
        Anonymizes text based on analyzer results.

        Returns:
            str: The anonymized text.
        """
        anonymizer_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_result,
        )
        return anonymizer_result.text
