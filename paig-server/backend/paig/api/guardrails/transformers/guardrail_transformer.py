import copy
from collections import defaultdict

from api.guardrails.api_schemas.guardrail import GRConfigView
from api.guardrails import GuardrailProvider
from api.guardrails.providers import GuardrailConfig
from api.guardrails.transformers.backend import GuardrailTransformerBase
from api.guardrails.transformers.backend.aws_gr_transformer import AWSGuardrailTransformer
from core.exceptions import BadRequestException


class GuardrailTransformer:
    @staticmethod
    def transform(guardrail_provider: GuardrailProvider, guardrail_configs: list[GRConfigView]) -> dict[str, list[GuardrailConfig]]:
        """
        Processes multiple guardrail configurations and returns a dict
        with provider names as keys and lists of transformed configs as values.

        Args:
            guardrail_provider (GuardrailProvider): The guardrail provider.
            guardrail_configs (list[GRConfigView]): A list of guardrail configurations.
        Returns:
            dict: Transformed configurations grouped by provider.
        """
        try:
            gr_transformer = GuardrailTransformerFactory.get_transformer(guardrail_provider.name)
            return {guardrail_provider.name: gr_transformer.transform(guardrail_configs)}
        except Exception as e:
            msg = f"{[e]}" if isinstance(e, KeyError) else str(e)
            raise BadRequestException(f"Failed to process guardrail configurations: {msg}")


class GuardrailTransformerFactory:
    @staticmethod
    def get_transformer(provider: str) -> GuardrailTransformerBase:
        transformers = {
            "AWS": AWSGuardrailTransformer
        }
        transformer_class = transformers.get(provider)
        if not transformer_class:
            raise ValueError(f"Unsupported provider: {provider}")
        return transformer_class()
