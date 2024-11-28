import copy
from collections import defaultdict

from api.guardrails.api_schemas.guardrail import GRConfigView
from api.guardrails import GuardrailProvider
from api.guardrails.providers import GuardrailConfig
from api.guardrails.transformers import GuardrailTransformer
from api.guardrails.transformers.backend.aws_gr_transformer import AWSGuardrailTransformer
from api.guardrails.transformers.backend.llama_gr_transformer import LlamaGuardrailTransformer
from core.exceptions import BadRequestException


class GuardrailTransformerProcessor:
    @staticmethod
    def process(guardrail_configs: list[GRConfigView]) -> dict[str, list[GuardrailConfig]]:
        """
        Processes multiple guardrail configurations and returns a dict
        with provider names as keys and lists of transformed configs as values.

        Args:
            guardrail_configs (list[GRConfigView]): A list of guardrail configurations.
        Returns:
            dict: Transformed configurations grouped by provider.
        """
        try:
            gr_provider_configs_map = defaultdict(list)
            [gr_provider_configs_map[config.guardrail_provider].append(config) for config in guardrail_configs]
            gr_configs = dict(gr_provider_configs_map)

            multi_configs = gr_provider_configs_map[GuardrailProvider.MULTIPLE]
            gr_providers = []
            if multi_configs:
                for gr_config in multi_configs:
                    sub_configs = gr_config.config_data.get('configs')
                    for sub_config in sub_configs:
                        provider = GuardrailProvider[sub_config['guardrailProvider']]
                        if provider not in gr_providers:
                            if provider not in gr_configs:
                                gr_configs[provider] = []
                            gr_configs[provider].append(copy.deepcopy(gr_config))
                gr_configs.pop(GuardrailProvider.MULTIPLE, None)

            transformed_results = {}
            for provider, configs in gr_configs.items():
                transformer = GuardrailTransformerFactory.get_transformer(provider.name)
                if provider.name not in transformed_results:
                    transformed_results[provider.name] = []
                transformed_results[provider.name].extend(transformer.transform(configs))

            return transformed_results
        except Exception as e:
            raise BadRequestException(f"Failed to process guardrail configurations: {str(e)}")


class GuardrailTransformerFactory:
    @staticmethod
    def get_transformer(provider: str) -> GuardrailTransformer:
        transformers = {
            "AWS": AWSGuardrailTransformer,
            "LLAMA": LlamaGuardrailTransformer
        }
        transformer_class = transformers.get(provider)
        if not transformer_class:
            raise ValueError(f"Unsupported provider: {provider}")
        return transformer_class()