import logging

from api.shield.model.scanner_result import ScannerResult
from api.shield.model.analyzer_result import AnalyzerResult
from api.shield.scanners.BaseScanner import Scanner
from profanity_check import predict_prob

logger = logging.getLogger(__name__)


class ToxicContentScanner(Scanner):
    """
    Scanner implementation for detecting toxic content in the input prompt.
    """

    def __init__(self, **kwargs):
        """
        Initialize the ToxicContentScanner with the specified parameters.

        Parameters:
            **kwargs: keyword arguments passed from properties file.
            E.g.
            name (str): The name of the scanner.
            request_types (list): List of request types that the scanner will handle.
            enforce_access_control (bool): Flag to enforce access control.
            model_path (str): Path to the model used by the scanner.
            model_score_threshold (float): Threshold score for the model to consider a match.
            entity_type (str): Type of entity the scanner is looking for.
            enable (bool): Flag to enable or disable the scanner.
        """
        super().__init__(**kwargs)

    def scan(self, message: str) -> ScannerResult:
        """
        Process the input prompt according to the specific scanner's implementation.

        Parameters:
            message (str): The input prompt that needs to be processed.

        Returns:
            dict: dictionary consisting of tags and other additional infos
        """
        score = predict_prob([message])
        is_safe = score[0] < self.model_score_threshold

        if not is_safe:
            analyzer_result = AnalyzerResult(start=0, end=len(message), entity_type=self.get_property('entity_type'), score=score[0],
                                         model_name='', scanner_name=self.get_property('name'), analysis_explanation=None,
                                         recognition_metadata=None)
            logger.debug(f"ToxicContentScanner: {self.entity_type} content detected in the input prompt.")
            return ScannerResult(traits=[self.entity_type], score=score, analyzer_result=[analyzer_result])

        logger.debug(f"ToxicContentScanner: {self.entity_type} not detected in the input prompt.")
        return ScannerResult(traits=[])
