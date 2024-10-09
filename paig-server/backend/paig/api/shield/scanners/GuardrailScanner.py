import logging
import boto3
import os

from api.shield.utils import config_utils
from api.shield.scanners.BaseScanner import Scanner

logger = logging.getLogger(__name__)


class GuardrailScanner(Scanner):
    """
    Scanner implementation for applying guard rail policies in the input prompt.
    """

    def __init__(self, name, request_types, enforce_access_control, model_path, model_score_threshold, entity_type,
                 enable, **kwargs):
        """
        Initialize the required models and variables for the scanner
        """
        super().__init__(name=name,
                         request_types=request_types,
                         enforce_access_control=enforce_access_control,
                         model_path=model_path,
                         model_score_threshold=model_score_threshold,
                         entity_type=entity_type,
                         enable=enable,
                         **kwargs)

        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name="us-east-1"
        )

    def scan(self, message: str):
        """
        Scan the input prompt through the Bedrock guardrail.

        Parameters:
            message (str): The input prompt that needs to be scanned.

        Returns:
            dict: Scan result including traits, actions, and output text if intervention occurs.
        """
        guardrail_id, guardrail_version = get_guardrail_details()

        response = self.bedrock_client.apply_guardrail(
            guardrailIdentifier=guardrail_id,
            guardrailVersion=guardrail_version,
            source='OUTPUT',
            content=[{'text': {'text': message}}]
        )

        if response.get('action') == 'GUARDRAIL_INTERVENED':
            outputs = response.get('outputs', [])
            output_text = outputs[0].get('text') if outputs else None

            tag_set, action_set = set(), set()
            for assessment in response.get('assessments', []):
                # Combine assessments processing for various policies
                _extract_assessment_info(assessment, tag_set, action_set)

            logger.debug(
                f"GuardrailService: Action required. Tags: {tag_set}, Actions: {action_set}, Output: {output_text}")
            return {"traits": list(tag_set), "actions": list(action_set), "output_text": output_text}

        logger.debug("GuardrailService: No action required.")
        return {}


def _extract_assessment_info(assessment, tag_set, action_set):
    """
        Extract relevant information from the assessment data.
        """
    for policy in ['sensitiveInformationPolicy', 'topicPolicy', 'contentPolicy', 'wordPolicy']:
        info = assessment.get(policy, {})
        for key in ['piiEntities', 'regexes', 'topics', 'filters', 'managedWordLists', 'customWords']:
            entities = info.get(key, [])
            extract_info(entities, tag_set, action_set)


def extract_info(entities, tag_set: set, action_set: set):
    """
    Extract tag and action info from entities.
    """
    for entity in entities:
        tag_set.add((entity.get('type') or entity.get('name') or entity.get('match', '')).upper())
        action_set.add(entity.get('action'))


def get_guardrail_details():
    """
    Fetch guardrail details
    """
    default_guardrail_id = config_utils.get_property_value('bedrock_guardrail_id')
    default_guardrail_version = config_utils.get_property_value('bedrock_guardrail_version')
    guardrail_id = os.environ.get('BEDROCK_GUARDRAIL_ID', default_guardrail_id)
    guardrail_version = os.environ.get('BEDROCK_GUARDRAIL_VERSION', default_guardrail_version)

    if not guardrail_id or not guardrail_version:
        logger.error("Guardrail ID or Guardrail Version not found in environment variables.")
        raise ValueError("Guardrail ID or Guardrail Version not found in environment variables.")

    return guardrail_id, guardrail_version
