from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

from api.guardrails.providers.models import GuardrailProviderType, GuardrailConnection, GuardrailConfig


class GuardrailProvider(ABC):
    """
    Abstract base class for defining a guardrail provider interface.

    This class defines the methods for verifying connection details, and creating,
    updating, and deleting guardrails. Any provider implementation must extend this class
    and implement the abstract methods.
    """

    def __init__(self, connection_details: Dict[str, str], **kwargs):
        """
        Initialize the GuardrailProvider with connection details.

        Args:
            connection_details (Dict[str, str]): A dictionary containing the necessary connection details.
            kwargs: Additional optional arguments.
        """
        self.connection_details = connection_details

    @abstractmethod
    def verify_connection_details(self, **kwargs) -> bool:
        """
        Verify the connection details.

        Args:
            kwargs: Additional optional arguments.

        Returns:
            bool: True if the connection details are valid, False otherwise.
        """
        pass

    @abstractmethod
    def create_guardrail(self, guardrail_configs: List['GuardrailConfig'], **kwargs) -> Tuple[bool, Dict]:
        """
        Create a guardrail using the provided configuration data.

        Args:
            guardrail_configs (List[GuardrailConfig]): A list of guardrail configuration objects.
            kwargs: Additional optional arguments.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a dictionary of created guardrail details.
        """
        pass

    @abstractmethod
    def update_guardrail(self, created_guardrail_details: Dict, updated_guardrail_configs: List['GuardrailConfig'],
                         **kwargs) -> Tuple[bool, Dict]:
        """
        Update an existing guardrail with new configurations.

        Args:
            created_guardrail_details (Dict): A dictionary containing details of the existing guardrail.
            updated_guardrail_configs (List[GuardrailConfig]): A list of updated guardrail configuration objects.
            kwargs: Additional optional arguments.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a dictionary of updated guardrail details.
        """
        pass

    @abstractmethod
    def delete_guardrail(self, created_guardrail_details: Dict, **kwargs) -> Tuple[bool, Dict]:
        """
        Delete an existing guardrail.

        Args:
            created_guardrail_details (Dict): A dictionary containing details of the guardrail to delete.
            kwargs: Additional optional arguments.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a dictionary with deletion status details.
        """
        pass


class GuardrailProviderManager:

    @staticmethod
    def verify_guardrails_connection_details(connections: List['GuardrailConnection'], **kwargs) -> bool:
        """
        Verifies the connection details for each guardrail provider.

        Args:
            connections (List[GuardrailConnection]): List of guardrail connections.
            **kwargs: Additional keyword arguments.

        Returns:
            bool: True if all connections are valid, False otherwise.
        """
        for connection in connections:
            if not GuardrailProviderManager._verify_connection_details(connection.guardrailProvider, connection.connectionDetails, **kwargs):
                return False
        return True

    @staticmethod
    def create_guardrail(connections: List['GuardrailConnection'], guardrail_configs: List['GuardrailConfig'], **kwargs) -> Dict[str, Dict]:
        """
        Creates guardrails for each provider.

        Args:
            connections (List[GuardrailConnection]): List of guardrail connections.
            guardrail_configs (List[GuardrailConfig]): List of guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the result of guardrail creation for each provider.
        """
        grouped_connections = GuardrailProviderManager._group_connections_by_provider(connections)
        grouped_guardrail_configs = GuardrailProviderManager._group_by_provider(guardrail_configs)

        guardrail_provider_map = GuardrailProviderManager._initialize_providers(grouped_connections, **kwargs)

        create_guardrails_response = {}
        successful_providers = set()

        for provider_type, guardrail_configs in grouped_guardrail_configs.items():
            provider = guardrail_provider_map[provider_type]
            success, response = provider.create_guardrail(guardrail_configs, **kwargs)
            create_guardrails_response[provider_type] = {
                "success": success,
                "response": response
            }

            if success:
                successful_providers.add(provider_type)

        # If any guardrail creation fails, roll back by deleting only the successfully created guardrails
        if len(create_guardrails_response) != len(successful_providers):
            for provider_type in successful_providers:
                success_response = create_guardrails_response[provider_type]
                if not success_response["success"]:
                    provider = guardrail_provider_map[provider_type]
                    provider.delete_guardrail(success_response, **kwargs)

        return create_guardrails_response

    @staticmethod
    def update_guardrail(connections: List['GuardrailConnection'], create_guardrails_response: Dict[str, Dict], updated_guardrails: List['GuardrailConfig'], **kwargs) -> Dict[str, Dict]:
        """
        Updates guardrails for each provider.

        Args:
            connections (List[GuardrailConnection]): List of guardrail connections.
            create_guardrails_response (Dict[str, Dict]): Response of previously created guardrails.
            updated_guardrails (List[GuardrailConfig]): List of updated guardrail configurations.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the result of the guardrail update for each provider.
        """
        grouped_connections = GuardrailProviderManager._group_connections_by_provider(connections)
        grouped_guardrail_configs = GuardrailProviderManager._group_by_provider(updated_guardrails)

        guardrail_provider_map = GuardrailProviderManager._initialize_providers(grouped_connections, **kwargs)

        update_guardrails_response = {}
        for provider_type, guardrail_configs in grouped_guardrail_configs.items():
            provider = guardrail_provider_map[provider_type]
            success, response = provider.update_guardrail(
                create_guardrails_response[provider_type],
                guardrail_configs,
                **kwargs
            )
            update_guardrails_response[provider_type] = {
                "success": success,
                "response": response
            }

        return update_guardrails_response

    @staticmethod
    def delete_guardrail(connections: List['GuardrailConnection'], create_guardrails_response: Dict[str, Dict], **kwargs) -> Dict[str, Dict]:
        """
        Deletes guardrails for each provider.

        Args:
            connections (List[GuardrailConnection]): List of guardrail connections.
            create_guardrails_response (Dict[str, Dict]): Response of previously created guardrails.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the result of the guardrail deletion for each provider.
        """
        grouped_connections = GuardrailProviderManager._group_connections_by_provider(connections)

        delete_guardrails_response = {}
        for provider_type, created_guardrail_details in create_guardrails_response.items():
            provider = GuardrailProviderManager._initialize_providers({provider_type: grouped_connections[provider_type]}, **kwargs)[provider_type]
            success, response = provider.delete_guardrail(created_guardrail_details, **kwargs)
            delete_guardrails_response[provider_type] = {
                "success": success,
                "response": response
            }

        return delete_guardrails_response

    @staticmethod
    def _verify_connection_details(provider: 'GuardrailProviderType', connection_details: Dict, **kwargs) -> bool:
        """
        Verifies the connection details for the given guardrail provider.

        Args:
            provider (GuardrailProviderType): The guardrail provider type.
            connection_details (Dict): Connection details for the provider.
            **kwargs: Additional keyword arguments.

        Returns:
            bool: True if the connection details are valid, False otherwise.
        """
        if provider == GuardrailProviderType.AWS:
            from backend.bedrock import BedrockGuardrailProvider
            provider_instance = BedrockGuardrailProvider(connection_details, **kwargs)
            return provider_instance.verify_connection_details()
        else:
            raise ValueError(f"Unknown guardrail provider: {provider}")

    @staticmethod
    def _initialize_providers(grouped_connections: Dict[str, 'GuardrailConnection'], **kwargs) -> Dict[str, 'GuardrailProvider']:
        """
        Initializes providers based on the connection details.

        Args:
            grouped_connections (Dict[str, GuardrailConnection]): Grouped connections by provider type.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, GuardrailProvider]: A dictionary mapping provider types to provider instances.
        """
        provider_map = {}
        for provider_type, connection in grouped_connections.items():
            if provider_type == 'AWS':
                from .backend.bedrock import BedrockGuardrailProvider
                provider_map[provider_type] = BedrockGuardrailProvider(connection.connectionDetails, **kwargs)
            else:
                raise ValueError(f"Unknown guardrail provider: {provider_type}")
        return provider_map

    @staticmethod
    def _group_connections_by_provider(connections: List['GuardrailConnection']) -> Dict[str, 'GuardrailConnection']:
        """
        Groups the connections by provider type.

        Args:
            connections (List[GuardrailConnection]): List of guardrail connections.

        Returns:
            Dict[str, GuardrailConnection]: A dictionary with connections grouped by provider type.
        """
        grouped = {}
        for connection in connections:
            provider = connection.guardrailProvider
            if provider not in grouped:
                grouped[provider] = connection
        return grouped

    @staticmethod
    def _group_by_provider(items: List['GuardrailConfig']) -> Dict[str, List['GuardrailConfig']]:
        """
        Groups the guardrail configurations by provider type.

        Args:
            items (List[GuardrailConfig]): List of guardrail configurations.

        Returns:
            Dict[str, List[GuardrailConfig]]: A dictionary with configurations grouped by provider type.
        """
        grouped = {}
        for item in items:
            provider = item.guardrailProvider
            if provider not in grouped:
                grouped[provider] = []
            grouped[provider].append(item)
        return grouped
