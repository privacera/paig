import logging

from api.guardrails.providers import GuardrailConfig
from api.guardrails.transformers import GuardrailTransformer


class LlamaGuardrailTransformer(GuardrailTransformer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)

    def transform(self, guardrail_configs: list[GuardrailConfig], **kwargs):
        """Transform the config into AWS Bedrock-specific format."""

        return guardrail_configs
