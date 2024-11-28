import logging

from api.guardrails.api_schemas.guardrail import GRConfigView
from api.guardrails import GuardrailConfigType
from api.guardrails.providers import GuardrailConfig as AWSGuardrailConfig, GuardrailConfig
from api.guardrails.transformers import GuardrailTransformer


class AWSGuardrailTransformer(GuardrailTransformer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)

    def transform(self, guardrail_configs: list[GRConfigView], **kwargs) -> list[GuardrailConfig]:
        """
        Transform the config into AWS Bedrock-specific format.

        Args:
            guardrail_configs (list[GRConfigView]): A list of guardrail configurations.
            kwargs: Additional optional arguments.
        """
        transformed_configs = []
        content_moderation_config = None
        prompt_attack_config = None
        for guardrail_config in guardrail_configs:
            transformed_config = None
            match guardrail_config.config_type:
                case GuardrailConfigType.CONTENT_MODERATION:
                    transformed_config = self._transform_content_moderation(guardrail_config)
                    content_moderation_config = transformed_config
                case GuardrailConfigType.SENSITIVE_DATA:
                    transformed_config = self._transform_sensitive_data(guardrail_config)
                case GuardrailConfigType.OFF_TOPIC:
                    transformed_config = self._transform_off_topic(guardrail_config)
                case GuardrailConfigType.DENIED_TERMS:
                    transformed_config = self._transform_denied_terms(guardrail_config)
                case GuardrailConfigType.PROMPT_SAFETY:
                    prompt_attack_config = guardrail_config
            if transformed_config is not None:
                transformed_configs.append(transformed_config)

        if prompt_attack_config is not None:
            transformed_prompt_safety = self._transform_prompt_safety(content_moderation_config, prompt_attack_config)
            if transformed_prompt_safety is not None:
                transformed_configs.append(transformed_prompt_safety)

        return transformed_configs

    def _transform_content_moderation(self, guardrail_config):
        try:
            aws_gr_config = AWSGuardrailConfig(configType="contentPolicyConfig", guardrailProvider="AWS", configData={})
            filters_config = list(dict())
            for config in guardrail_config.config_data['configs']:
                if config['guardrailProvider'] == "AWS":
                    filters_config.append({
                        "type": config['category'].upper(),
                        "inputStrength": config['filterStrengthPrompt'].upper(),
                        "outputStrength": config['filterStrengthResponse'].upper()
                    })
            if filters_config is None:
                return None
            aws_gr_config.configData['filtersConfig'] = filters_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in content moderation config: {str(e)}")

    def _transform_sensitive_data(self, guardrail_config):
        try:
            aws_gr_config = AWSGuardrailConfig(configType="sensitiveInformationPolicyConfig", guardrailProvider="AWS", configData={})
            pii_entities_config = []
            for config in guardrail_config.config_data['configs']:
                if config['action'].upper() == "DENY":
                    action = "BLOCK"
                elif config['action'].upper() == "REDACT":
                    action = "ANONYMIZE"
                else:
                    continue
                pii_entities_config.append({
                    "type": config['category'],
                    "action": action
                })
            if pii_entities_config is None:
                return None
            aws_gr_config.configData['piiEntitiesConfig'] = pii_entities_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in sensitive data config: {str(e)}")

    def _transform_off_topic(self, guardrail_config):
        try:
            aws_gr_config = AWSGuardrailConfig(configType="topicPolicyConfig", guardrailProvider="AWS", configData={})
            topic_policy_config = []
            for config in guardrail_config.config_data['configs']:
                topic_policy_config.append({
                    "name": config['topic'],
                    "definition": config['definition'],
                    "examples": config['samplePhrases'],
                    "type": "DENY"
                })
            if topic_policy_config is None:
                return None
            aws_gr_config.configData['topicsConfig'] = topic_policy_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in off topic config: {str(e)}")

    def _transform_denied_terms(self, guardrail_config):
        try:
            aws_gr_config = AWSGuardrailConfig(configType="wordPolicyConfig", guardrailProvider="AWS", configData={})
            word_policy_config = []
            aws_gr_config.configData['managedWordListsConfig'] = [{"type": "PROFANITY"}]
            for config in guardrail_config.config_data['configs']:
                word_policy_config.append({"text": config['term']})
                for term in config['keywords']:
                    word_policy_config.append({"text": term})
            if word_policy_config is None:
                return None
            aws_gr_config.configData['wordsConfig'] = word_policy_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in denied terms config: {str(e)}")

    def _transform_prompt_safety(self, content_moderation_config, prompt_attack_config):
        try:
            if content_moderation_config is not None:
                content_moderation_config.configData['filtersConfig'].append({
                    "type": "PROMPT_ATTACK",
                    "inputStrength": prompt_attack_config.config_data['configs'][0]['filterStrengthPrompt'].upper(),
                    "outputStrength": "NONE"
                })
                return None
            else:
                return self._transform_content_moderation(prompt_attack_config)
        except Exception as e:
            raise Exception(f"Invalid data in prompt safety config: {str(e)}")
