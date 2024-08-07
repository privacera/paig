from abc import ABC, abstractmethod


class IAccountServiceClient(ABC):
    """
      Interface for fetching encryption keys.

      Methods:
          get_all_encryption_keys(tenant_id):
              Fetches all encryption keys for the specified `tenant_id`.
      """
    @abstractmethod
    def get_all_encryption_keys(self, tenant_id):
        """Abstract method to be implemented by subclasses."""
        pass
