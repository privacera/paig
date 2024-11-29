import logging
import boto3
import os

from api.shield.enum.ShieldEnums import Guardrail, RequestType
from api.shield.model.scanner_result import ScannerResult
from api.shield.model.analyzer_result import AnalyzerResult
from api.shield.scanners.BaseScanner import Scanner

logger = logging.getLogger(__name__)


class AWSBedrockGuardrailScanner(Scanner):
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
        Scan the input prompt through the Bedrock guardrail.

        Parameters:
            message (str): The input prompt that needs to be scanned.

        Returns:
            dict: Scan result including traits, actions, and output text if intervention occurs.
        """
        guardrail_id, guardrail_version, region = self._get_guardrail_details()
        if not guardrail_id or not guardrail_version or not region:
            logger.error("AWSBedrockGuardrailScanner: Guardrail details not found. Hence skipping the scan.")
            return ScannerResult(traits=[])

        bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=region
        )
        guardrail_source = Guardrail.INPUT.value if self.get_property('scan_for_req_type') in [
            RequestType.PROMPT.value,
            RequestType.ENRICHED_PROMPT.value,
            RequestType.RAG.value
        ] else Guardrail.OUTPUT.value
        logger.debug(f"AWSBedrockGuardrailScanner: Scanning message: {message} with guardrail source: {guardrail_source} for {self.get_property('scan_for_req_type')}")

        response = bedrock_client.apply_guardrail(
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version,
            source=guardrail_source,
            content=[{'text': {'text': message}}]
        )
        logger.info(f"AWSBedrockGuardrailScanner: Response received: {response}")

        if response.get('action') == Guardrail.GUARDRAIL_INTERVENED.value:
            outputs = response.get('outputs', [])
            output_text = outputs[0].get('text') if outputs else None
            tag_set, action_set = self._extract_and_populate_assessment_info(response.get('assessments', []))

            analyzer_result = AnalyzerResult(start=0, end=len(message), entity_type='AWSBEDROCKGUARDRAIL', score=1.0,
                                         model_name='', scanner_name=self.get_property('name'), analysis_explanation=None,
                                         recognition_metadata=response)

            logger.info(f"AWSBedrockGuardrailScanner: Action required. Tags: {tag_set}, Actions: {action_set}")
            logger.debug(f"AWSBedrockGuardrailScanner: Action required. Output: {output_text}")
            return ScannerResult(traits=list(tag_set), actions=list(action_set), output_text= output_text, analyzer_result=[analyzer_result])

        logger.info("AWSBedrockGuardrailScanner: No action required for the message.")
        return ScannerResult(traits=[])

    def _get_guardrail_details(self) -> (str, str, str):
        """
        Fetch guardrail details
        """
        default_guardrail_id = self.get_property('guardrail_id')
        default_guardrail_version = self.get_property('guardrail_version')
        default_region = self.get_property('region')
        guardrail_id = os.environ.get('BEDROCK_GUARDRAIL_ID', default_guardrail_id)
        guardrail_version = os.environ.get('BEDROCK_GUARDRAIL_VERSION', default_guardrail_version)
        region = os.environ.get('BEDROCK_REGION', default_region)

        if not guardrail_id:
            logger.error("Bedrock Guardrail ID not found in properties or environment variables.")
        if not guardrail_version:
            logger.error("Bedrock Guardrail version not found in properties or environment variables.")
        if not region:
            logger.error("Bedrock Guardrail region not found in properties or environment variables.")

        return guardrail_id, guardrail_version, region

    # noinspection PyMethodMayBeStatic
    def _extract_and_populate_assessment_info(self, assessments: list) -> (set, set):
        """
        Extract relevant information from the assessment data.
        """
        tag_set, action_set = set(), set()
        for policy in assessments:
            for policy_key, policy_data in policy.items():
                for data_key, policy_data_value in policy_data.items():
                    for value in policy_data_value:
                        # Extract the tag data from the policy
                        tag_data = (value.get('type') or value.get('name') or value.get('match', '')).replace(' ', '_').upper()
                        # If the tag data is 'DENY' that indicates there's a off topic policy, hence extract the name of the policy
                        if tag_data == "DENY":
                            tag_data = value.get('name').replace(' ', '_').upper()
                        tag_set.add(tag_data)
                        action_set.add(value.get('action'))
        return tag_set, action_set
