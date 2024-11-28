from abc import ABC

from api.guardrails.providers import GuardrailConfig
from api.guardrails.transformers.backend.aws_gr_transformer import AWSGuardrailTransformer


class GuardrailTransformer(ABC):
    """
    Abstract base class for defining a guardrail transformer interface.

    This class defines the methods for transforming guardrail configurations.
    """

    def __init__(self, **kwargs):
        """
        Initialize the GuardrailTransformer.

        Args:
            kwargs: Additional optional arguments.
        """
        pass

    def transform(self, guardrail_configs: list[GuardrailConfig], **kwargs) -> list[GuardrailConfig]:
        """
        Transform the guardrail configurations.

        Args:
            guardrail_configs (list[GuardrailConfig]): A list of guardrail configurations.
            kwargs: Additional optional arguments.

        Returns:
            list[GuardrailConfig]: The transformed guardrail configurations.
        """
        pass


class GuardrailTransformerFactory:
    @staticmethod
    def get_transformer(provider: str) -> GuardrailTransformer:
        transformers = {
            "AWS": AWSGuardrailTransformer
        }
        transformer_class = transformers.get(provider)
        if not transformer_class:
            raise ValueError(f"Unsupported provider: {provider}")
        return transformer_class()
