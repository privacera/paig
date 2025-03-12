from api.shield.interfaces.governance_service_interface import IGovernanceServiceClient
from core.utils import SingletonDepends


class LocalGovernanceServiceClient(IGovernanceServiceClient):
    """
    Local client implementation for fetching AWS Bedrock Guardrail info.

    Methods:
        get_application_guardrail_name(tenant_id, application_key):
            Retrieves AWS Bedrock Guardrail names for the specified tenant and application key from a local data source.
    """

    def __init__(self):
        """
        Initialize the local governance service client.
        """
        from api.governance.services.ai_app_service import AIAppService
        self.ai_application_service: AIAppService = SingletonDepends(AIAppService)

    async def get_application_guardrail_name(self, tenant_id, application_key) -> list:
        """
        Retrieve all AWS Bedrock Guardrail names associated with the specified `tenant_id` and 'application_key'

        Args:
            tenant_id (str): The identifier of the tenant whose AWS Bedrock Guardrail details are to be fetched.
            application_key (str): The identifier of the application for which AWS Bedrock Guardrail details are to be fetched.

        Returns:
            List: AWS Bedrock Guardrail names associated with the specified `tenant_id` and 'application_key'.
        """
        result = await self.ai_application_service.get_ai_application_by_application_key(application_key)
        if result:
            return result.guardrails  if result.guardrails else []
        else:
            return []
