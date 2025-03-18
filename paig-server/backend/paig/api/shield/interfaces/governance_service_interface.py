from abc import ABC, abstractmethod


class IGovernanceServiceClient(ABC):
    """
      Interface for fetching AWS Bedrock Guardrail details.

      Methods:
          get_application_guardrail_name(tenant_id, application_key):
              Fetches all AWS Bedrock Guardrail names associated with the specified `tenant_id` and 'application_key'
      """
    @abstractmethod
    def get_application_guardrail_name(self, tenant_id, application_key) -> list:
        """Abstract method to be implemented by subclasses."""
        pass
