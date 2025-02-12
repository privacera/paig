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
            return result.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        else:
            return {}

    async def get_guardrail_info_by_application_key(self, tenant_id, application_key, last_known_version):
        """"""
        result = await self.guardrail_service.get_all_by_app_key(application_key, last_known_version)
        if result:
            return result.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        else:
            return {}
