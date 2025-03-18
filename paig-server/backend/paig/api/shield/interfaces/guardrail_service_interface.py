from abc import ABC, abstractmethod


class IGuardrailServiceClient(ABC):
    """
    Interface for fetching Guardrail Config info.

    Methods:
        get_guardrail_info_by_id(tenant_id: str, guardrail_id: int):
            Retrieves Guardrail Config details for the specific tenant and guardrail id from respective data sources.
        get_guardrail_info_by_name(tenant_id: str, guardrail_name: str):
            Retrieves Guardrail Config details for the specified tenant and guardrail name from respective data sources.
    """
    @abstractmethod
    def get_guardrail_info_by_id(self, tenant_id: str, guardrail_id: int):
        """Abstract method to be implemented by subclasses."""
        pass

    @abstractmethod
    def get_guardrail_info_by_name(self, tenant_id:str, guardrail_name: str):
        """Abstract method to be implemented by subclasses."""
        pass
