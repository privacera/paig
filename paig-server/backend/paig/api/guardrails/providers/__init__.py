from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

from api.guardrails.providers.models import GuardrailProviderType, GuardrailConnection, GuardrailConfig, \
    CreateGuardrailRequest, UpdateGuardrailRequest, DeleteGuardrailRequest


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
            kwargs: Additional optional arguments.
        """
        self.connection_details = connection_details

    @abstractmethod
    def verify_connection_details(self, **kwargs) -> Tuple[bool, Dict]:
        """
        Verify the connection details.

        Args:
            kwargs: Additional optional arguments.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a dictionary of connection evaluation details.
        """
        pass

    @abstractmethod
    def create_guardrail(self, request: 'CreateGuardrailRequest', **kwargs) -> Tuple[bool, Dict]:
        """
        Create a guardrail using the provided configuration data.

        Args:
            request (CreateGuardrailRequest): A request object containing guardrail configurations.
            kwargs: Additional optional arguments.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a dictionary of created guardrail details.
        """
        pass

    @abstractmethod
    def update_guardrail(self, request: 'UpdateGuardrailRequest', **kwargs) -> Tuple[bool, Dict]:
        """
        Update an existing guardrail with new configurations.

        Args:
            request (UpdateGuardrailRequest): A request object containing updated guardrail configurations.
            kwargs: Additional optional arguments.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a dictionary of updated guardrail details.
        """
        pass

    @abstractmethod
    def delete_guardrail(self, request: 'DeleteGuardrailRequest', **kwargs) -> Tuple[bool, Dict]:
        """
        Delete an existing guardrail.

        Args:
            request (DeleteGuardrailRequest): A request object containing guardrail details.
            kwargs: Additional optional arguments.

        Returns:
            Tuple[bool, Dict]: A tuple containing a success flag and a dictionary with deletion status details.
        """
        pass


class GuardrailProviderManager:
    """
    Manages operations for multiple guardrail providers.

    This class provides methods for verifying connection details, and creating, updating, and deleting guardrails
    for multiple guardrail providers.
    """

    @staticmethod
    def process_guardrail_request(
        request: Dict[str, Any],
        operation: str,
        **kwargs
    ) -> Dict[str, Dict]:
        """
        Processes a guardrail request for multiple providers.

        Args:
            request (Dict[str, Any]): A dictionary containing the request data for each provider.
            operation (str): The operation to perform ('verify', 'create', 'update', 'delete').
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the results of the operation for each provider.
        """
        response = {}

        for provider_name, guardrail_request in request.items():
            connection_details = getattr(guardrail_request, "connectionDetails", {})
            provider: GuardrailProvider = GuardrailProviderManager._get_provider_instance(
                provider_name, connection_details, **kwargs
            )

            operation_method = getattr(provider, f"{operation}_guardrail", None)
            if not callable(operation_method):
                raise AttributeError(f"{provider.__class__.__name__} does not implement '{operation}_guardrail'")

            success, response_data = operation_method(guardrail_request, **kwargs)

            response[provider_name] = {
                "success": success,
                "response": response_data
            }

        return response

    @staticmethod
    def verify_guardrails_connection_details(request: Dict[str, 'GuardrailConnection'], **kwargs) -> Dict[str, Dict]:
        """
        Verifies connection details for each guardrail provider.

        Args:
            request (Dict[str, GuardrailConnection]): A dictionary containing the connection details for each provider.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the verification results for each provider.
        """
        return GuardrailProviderManager.process_guardrail_request(request, "verify", **kwargs)

    @staticmethod
    def create_guardrail(request: Dict[str, 'CreateGuardrailRequest'], **kwargs) -> Dict[str, Dict]:
        """
        Creates guardrails for each provider.

        Args:
            request (Dict[str, CreateGuardrailRequest]): A dictionary containing the request to create guardrails.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the results of guardrail creation for each provider.
        """
        return GuardrailProviderManager.process_guardrail_request(request, "create", **kwargs)

    @staticmethod
    def update_guardrail(request: Dict[str, 'UpdateGuardrailRequest'], **kwargs) -> Dict[str, Dict]:
        """
        Updates guardrails for each provider.

        Args:
            request (Dict[str, UpdateGuardrailRequest]): A dictionary containing the request to update guardrails.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the results of guardrail updates for each provider.
        """
        return GuardrailProviderManager.process_guardrail_request(request, "update", **kwargs)

    @staticmethod
    def delete_guardrail(request: Dict[str, 'DeleteGuardrailRequest'], **kwargs) -> Dict[str, Dict]:
        """
        Deletes guardrails for each provider.

        Args:
            request (Dict[str, DeleteGuardrailRequest]): A dictionary containing the request to delete guardrails.
            **kwargs: Additional keyword arguments.

        Returns:
            Dict[str, Dict]: A dictionary with the results of guardrail deletion for each provider.
        """
        return GuardrailProviderManager.process_guardrail_request(request, "delete", **kwargs)

    @staticmethod
    def _get_provider_instance(provider: str, connection_details: Dict, **kwargs) -> 'GuardrailProvider':
        """
        Returns an instance of the guardrail provider based on the provider type.

        Args:
            provider (str): The guardrail provider type.
            connection_details (Dict): Connection details for the provider.
            **kwargs: Additional keyword arguments.

        Returns:
            GuardrailProvider: An instance of the guardrail provider.
        """
        if provider == GuardrailProviderType.AWS:
            from api.guardrails.providers.backend.bedrock import BedrockGuardrailProvider
            return BedrockGuardrailProvider(connection_details, **kwargs)
        else:
            raise ValueError(f"Unknown guardrail provider: {provider}")