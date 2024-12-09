from abc import ABC

from api.guardrails.providers import GuardrailConfig


class GuardrailTransformerBase(ABC):
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
