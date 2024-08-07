import logging

from presidio_analyzer import AnalyzerEngine

from api.shield.presidio.nlp_handler import NLPHandler
from api.shield.utils import config_utils

SUPPORTED_LANG = ["en"]

logger = logging.getLogger(__name__)


class PresidioAnalyzerEngine:

    def __init__(self):
        self.score_threshold = config_utils.get_property_value_float('presidio_analyzer_score_threshold')
        self.entities = config_utils.get_property_value('presidio_analyzer_entities')

        nlp_engine = NLPHandler().get_engine()

        # configure presidio logger
        presidio_logger = logging.getLogger("presidio-analyzer")
        presidio_log_level = logging.getLevelName(config_utils.get_property_value("presidio_log_level", "INFO"))
        presidio_logger.setLevel(presidio_log_level)

        self.analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["en"]
        )
        self.remove_unwanted_recognizers()

    def remove_unwanted_recognizers(self):
        """
        Remove unwanted recognizers from the analyzer
        the method reads the property value presidio_recognizers_to_remove,
        loops through it and removes the recognizers from the analyzer registry matching the name
        :return:
        """
        logger.debug("Removing unwanted recognizers")
        # Get the recognizers to remove from the properties file
        recognisers = config_utils.get_property_value("presidio_recognizers_to_remove", None)
        if recognisers is not None:
            recognisers = recognisers.split(",")
            for recogniser in recognisers:
                # Remove the recognizer from the analyzer registry
                self.analyzer.registry.remove_recognizer(recogniser)
        else:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("No recognizers found to remove")

    def analyze(self, text: str):
        """
        Analyze the given text using the presidio analyzer
        :param text:
        :return: list of RecognizerResult as analyzer result
        """
        logger.debug("Analyzing starting")
        analyzer_result = self.analyzer.analyze(
            text=text,
            entities=None,
            language="en",
            score_threshold=self.score_threshold)
        logger.debug("Analyzing completed")
        return analyzer_result
