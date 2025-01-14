from api.shield.interfaces.guardrail_service_interface import IGuardrailServiceClient
from core.utils import SingletonDepends


class LocalGuardrailServiceClient(IGuardrailServiceClient):
    """
    Local client implementation for fetching Guardrail Config info.

    Methods:
        get_guardrail_info(guardrail_id):
            Retrieves Guardrail Config details for the specified guardrail id from a local data source.
    """

    def __init__(self):
        """
        Initialize the local guardrail service client.
        """
        from api.guardrails.services.guardrails_service import GuardrailService
        self.guardrail_service: GuardrailService = SingletonDepends(GuardrailService)

    async def get_guardrail_info(self, tenant_id, guardrail_id):
        """"""
        result = await self.guardrail_service.get_by_id(guardrail_id, extended=True)
        if result:
            return result.model_dump_json()
        else:
            return {}
