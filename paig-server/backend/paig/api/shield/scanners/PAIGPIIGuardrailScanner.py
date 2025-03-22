import logging

from api.shield.model.scanner_result import ScannerResult
from api.shield.scanners.BaseScanner import Scanner

logger = logging.getLogger(__name__)


class PAIGPIIGuardrailScanner(Scanner):
    """
    Scanner implementation for applying guard rail policies in the input prompt.
    """

    def __init__(self, **kwargs):
        """
        Initialize the GuardrailScanner with the specified parameters.

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
        Scan the input prompt through the PII guardrail.

        Parameters:
            message (str): The input prompt that needs to be scanned.

        Returns:
            dict: Scan result including traits, actions, and output text if intervention occurs.
        """
        # do pii guardrail evaluation
        pii_traits = self.get_property("pii_traits")
        sensitive_data_config = self.get_property("sensitive_data_config")

        from api.shield.services.guardrail_service import paig_pii_guardrail_evaluation
        deny_policies_list , redact_policies_dict = paig_pii_guardrail_evaluation(sensitive_data_config, pii_traits)

        if len(deny_policies_list) > 0:
            return ScannerResult(traits=[], actions=["BLOCKED"], output_text=sensitive_data_config.get("response_message"))
        if len(redact_policies_dict) > 0:
            return ScannerResult(traits=[], actions=["ANONYMIZED"], masked_traits=redact_policies_dict)

        return ScannerResult(traits=[])