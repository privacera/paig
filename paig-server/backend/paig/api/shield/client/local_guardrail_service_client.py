from api.shield.interfaces.guardrail_service_interface import IGuardrailServiceClient
from core.controllers.paginated_response import Pageable
from core.utils import SingletonDepends


class LocalGuardrailServiceClient(IGuardrailServiceClient):
    """
    Local client implementation for fetching Guardrail Config info.

    Methods:
        get_guardrail_info_by_id(tenant_id: str, guardrail_id: int):
            Retrieves Guardrail Config details for the specific tenant and guardrail id from local data sources.

        get_guardrail_info_by_name(tenant_id: str, guardrail_name: str):
            Retrieves Guardrail Config details for the specified tenant and guardrail name from local data sources.
    """

    def __init__(self):
        """
        Initialize the local guardrail service client.
        """
        from api.guardrails.services.guardrails_service import GuardrailService
        self.guardrail_service: GuardrailService = SingletonDepends(GuardrailService)

    async def get_guardrail_info_by_id(self, tenant_id: str, guardrail_id: int):
        """
        Retrieve Guardrail Config details for the specified guardrail id from the local data source.
        :param tenant_id:
        :param guardrail_id:
        :return:
        """
        result = await self.guardrail_service.get_by_id(guardrail_id, extended=True)
        if result:
            return result.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        else:
            return {}

    async def get_guardrail_info_by_name(self, tenant_id: str, guardrail_name: list):
        """
        Retrieve Guardrail Config details for the specified guardrail name from the local data source.
        :param tenant_id:
        :param guardrail_name:
        :return:
        """
        from api.guardrails.api_schemas.guardrail import GuardrailView, GuardrailFilter
        guardrail_filter = GuardrailFilter(name=guardrail_name[0], extended=True)
        result: Pageable = await self.guardrail_service.list(filter=guardrail_filter)
        if not result.empty:
            guardrail_info: GuardrailView = result.content[0]
            return guardrail_info.model_dump(mode="json", exclude_none=True, exclude_unset=True)
        else:
            return {}
