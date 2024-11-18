from abc import ABC, abstractmethod


class IGovernanceServiceClient(ABC):
    """
      Interface for fetching AWS Bedrock Guardrail details.

      Methods:
          get_aws_bedrock_guardrail_info(tenant_id, application_key):
              Fetches all encryption keys for the specified `tenant_id` and 'application_key'.
      """
    @abstractmethod
    def get_aws_bedrock_guardrail_info(self, tenant_id):
        """Abstract method to be implemented by subclasses."""
        pass
