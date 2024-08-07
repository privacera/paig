import logging

from api.shield.scanners.BaseScanner import Scanner
from profanity_check import predict_prob

logger = logging.getLogger(__name__)


class ToxicContentScanner(Scanner):
    """
    Scanner implementation for detecting toxic content in the input prompt.
    """

    def __init__(self, name, request_types, enforce_access_control, model_path, model_score_threshold, entity_type,
                 enable, **kwargs):
        """
        Initialize the required models and variables for the scanner
        """
        super().__init__(name, request_types, enforce_access_control, model_path, model_score_threshold, entity_type,
                         enable, **kwargs)

    def scan(self, message: str) -> dict:
        """
        Process the input prompt according to the specific scanner's implementation.

        Parameters:
            message (str): The input prompt that needs to be processed.

        Returns:
            dict: dictionary consisting of tags and other additional infos
        """
        score = predict_prob([message])
        is_safe = score < self.model_score_threshold

        if not is_safe:
            logger.debug(f"ToxicContentScanner: {self.entity_type} content detected in the input prompt.")
            return {"traits": [self.entity_type], "score": score}

        logger.debug(f"ToxicContentScanner: {self.entity_type} not detected in the input prompt.")
        return {}
