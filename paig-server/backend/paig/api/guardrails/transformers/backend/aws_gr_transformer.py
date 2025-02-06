import logging

from api.guardrails.api_schemas.guardrail import GRConfigView
from api.guardrails import GuardrailConfigType
from api.guardrails.providers import GuardrailConfig
from api.guardrails.transformers.backend import GuardrailTransformerBase


class AWSGuardrailTransformer(GuardrailTransformerBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)
        self.content_moderation_categories = ["HATE", "INSULTS", "SEXUAL", "VIOLENCE", "MISCONDUCT"]

    def transform(self, guardrail_configs: list[GuardrailConfig], **kwargs) -> list[GuardrailConfig]:
        """
        Transform the config into AWS Bedrock-specific format.

        Args:
            guardrail_configs (list[GRConfigView]): A list of guardrail configurations.
            kwargs: Additional optional arguments.
        """
        transformed_configs: list[GuardrailConfig] = []
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

    def _transform_content_moderation(self, content_moderation_config):
        try:
            aws_gr_config = GuardrailConfig(configType="contentPolicyConfig", guardrailProvider="AWS", configData={})
            filters_config = list(dict())
            added_categories = []
            for config in content_moderation_config.config_data['configs']:
                category = config['category'].upper()
                filters_config.append({
                    "type": category,
                    "inputStrength": config['filterStrengthPrompt'].upper(),
                    "outputStrength": config['filterStrengthResponse'].upper()
                })
                added_categories.append(category)

            if added_categories:
                for category in self.content_moderation_categories:
                    if category not in added_categories:
                        filters_config.append({"type": category, "inputStrength": "NONE", "outputStrength": "NONE"})

            if not filters_config:
                return None
            aws_gr_config.configData['filtersConfig'] = filters_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in content moderation config: {[e]}")

    def _transform_sensitive_data(self, sensitive_data_config):
        try:
            aws_gr_config = GuardrailConfig(configType="sensitiveInformationPolicyConfig", guardrailProvider="AWS", configData={})
            regex_entities_config = []
            for config in sensitive_data_config.config_data['configs']:
                if config['action'].upper() == "DENY":
                    action = "BLOCK"
                elif config['action'].upper() == "REDACT":
                    action = "ANONYMIZE"
                else:
                    continue
                if 'type' in config and config['type'].upper() == "REGEX":
                    regex_conf = {
                        "name": config['name'],
                        "pattern": config['pattern'],
                        "action": action
                    }
                    if 'description' in config:
                        regex_conf['description'] = config['description']
                    regex_entities_config.append(regex_conf)

            if not regex_entities_config:
                return None
            aws_gr_config.configData['regexesConfig'] = regex_entities_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in sensitive data config: {[e]}")

    def _transform_off_topic(self, off_topic_config):
        try:
            aws_gr_config = GuardrailConfig(configType="topicPolicyConfig", guardrailProvider="AWS", configData={})
            topic_policy_config = []
            for config in off_topic_config.config_data['configs']:
                topic_policy_config.append({
                    "name": config['topic'],
                    "definition": config['definition'],
                    "examples": config['samplePhrases'],
                    "type": "DENY"
                })
            if not topic_policy_config:
                return None
            aws_gr_config.configData['topicsConfig'] = topic_policy_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in off topic config: {[e]}")

    def _transform_denied_terms(self, denied_terms_config):
        try:
            aws_gr_config = GuardrailConfig(configType="wordPolicyConfig", guardrailProvider="AWS", configData={})
            word_policy_config = []
            profanity_config = []
            for config in denied_terms_config.config_data['configs']:
                if 'type' in config and config['type'].upper() == "PROFANITY" and config['value'] is True:
                    profanity_config.append({"type": "PROFANITY"})
                if 'term' in config:
                    word_policy_config.append({"text": config['term']})
                    for term in config['keywords']:
                        word_policy_config.append({"text": term})
            if not word_policy_config and not profanity_config:
                return None
            if word_policy_config:
                aws_gr_config.configData['wordsConfig'] = word_policy_config
            if profanity_config:
                aws_gr_config.configData['managedWordListsConfig'] = profanity_config
            return aws_gr_config
        except Exception as e:
            raise Exception(f"Invalid data in denied terms config: {[e]}")

    def _transform_prompt_safety(self, content_moderation_config, prompt_attack_config):
        try:
            if not prompt_attack_config.config_data['configs']:
                return None
            if content_moderation_config is not None:
                content_moderation_config.configData['filtersConfig'].append({
                    "type": "PROMPT_ATTACK",
                    "inputStrength": prompt_attack_config.config_data['configs'][0]['filterStrengthPrompt'].upper(),
                    "outputStrength": "NONE"
                })
                return None
            else:
                prompt_attack_config.config_data['configs'][0]['filterStrengthResponse'] = "NONE"
                return self._transform_content_moderation(prompt_attack_config)
        except Exception as e:
            msg = f"{[e]}" if isinstance(e, KeyError) else str(e)
            raise Exception(f"Invalid data in prompt safety config: {msg}")
