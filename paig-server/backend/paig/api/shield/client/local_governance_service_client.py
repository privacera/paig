import json
from api.shield.interfaces.governance_service_interface import IGovernanceServiceClient
from core.utils import SingletonDepends


class LocalGovernanceServiceClient(IGovernanceServiceClient):
    """
    Local client implementation for fetching AWS Bedrock Guardrail info.

    Methods:
        get_aws_bedrock_guardrail_info(tenant_id, application_key):
            Retrieves AWS Bedrock Guardrail details for the specified tenant and application key from a local data source.
    """

    def __init__(self):
        """
        Initialize the local governance service client.
        """
        from api.governance.services.ai_app_service import AIAppService
        self.ai_application_service: AIAppService = SingletonDepends(AIAppService)

    async def get_aws_bedrock_guardrail_info(self, tenant_id, application_key):
        """
        Retrieve all encryption keys for a specific tenant from the underlying data source.

        Args:
            tenant_id (str): The identifier of the tenant whose AWS Bedrock Guardrail details are to be fetched.
            application_key (str): The identifier of the application for which AWS Bedrock Guardrail details are to be fetched.

        Returns:
            dict: AWS Bedrock Guardrail details associated with the specified `tenant_id` and 'application_key'.
        """
        result = await self.ai_application_service.get_ai_application_by_application_key(application_key)
        if result.guardrail_details:
            return json.loads(result.guardrail_details)
        else:
            return {}
