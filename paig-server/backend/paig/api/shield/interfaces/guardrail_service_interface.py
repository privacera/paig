from abc import ABC, abstractmethod


class IGuardrailServiceClient(ABC):
    """
    Interface for fetching Guardrail Config info.

    Methods:
        get_guardrail_info(guardrail_id):
            Retrieves Guardrail Config details for the specified guardrail id from a local data source.
    """
    @abstractmethod
    def get_guardrail_info(self, tenant_id, guardrail_id):
        """Abstract method to be implemented by subclasses."""
        pass
