from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.guardrails.api_schemas.gr_sensitive_data import GRSensitiveDataView, GRSensitiveDataFilter
from api.guardrails.services.gr_sensitive_data_service import GRSensitiveDataService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from core.utils import SingletonDepends


class GRSensitiveDataController:
    """
    Controller class specifically for handling Guardrail Sensitive Data entities.

    Args:
        gr_sensitive_data_service (GRSensitiveDataService): The service class for handling Guardrail Sensitive Data entities.
    """

    def __init__(self,
                 gr_sensitive_data_service: GRSensitiveDataService = SingletonDepends(GRSensitiveDataService),
                 gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil)):
        self.gr_sensitive_data_service = gr_sensitive_data_service
        self.gov_service_validation_util = gov_service_validation_util

    async def list_gr_sensitive_datas(self, filter: GRSensitiveDataFilter, page_number: int, size: int,
                        sort: List[str]) -> Pageable:
        """
        List Guardrail Sensitive Data based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (GRSensitiveDataFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of Guardrail Sensitive Data.
        """
        return await self.gr_sensitive_data_service.list_gr_sensitive_datas(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_gr_sensitive_data(self, request: GRSensitiveDataView) -> GRSensitiveDataView:
        """
        Create a new Guardrail Sensitive Data.

        Args:
            request (GRSensitiveDataView): The view object representing the Guardrail Sensitive Data to create.

        Returns:
            GRSensitiveDataView: The created Guardrail Sensitive Data view object.
        """
        return await self.gr_sensitive_data_service.create_gr_sensitive_data(request)

    async def get_gr_sensitive_data_by_id(self, id: int) -> GRSensitiveDataView:
        """
        Retrieve Guardrail Sensitive Data by its ID.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to retrieve.

        Returns:
            GRSensitiveDataView: The Guardrail Sensitive Data view object corresponding to the ID.
        """
        return await self.gr_sensitive_data_service.get_gr_sensitive_data_by_id(id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_gr_sensitive_data(self, id: int, request: GRSensitiveDataView) -> GRSensitiveDataView:
        """
        Update Guardrail Sensitive Data identified by its ID.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to update.
            request (GRSensitiveDataView): The updated view object representing the Guardrail Sensitive Data.

        Returns:
            GRSensitiveDataView: The updated Guardrail Sensitive Data view object.
        """
        return await self.gr_sensitive_data_service.update_gr_sensitive_data(id, request)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_gr_sensitive_data(self, id: int):
        """
        Delete Guardrail Sensitive Data by its ID.

        Args:
            id (int): The ID of the Guardrail Sensitive Data to delete.
        """
        await self.gr_sensitive_data_service.delete_gr_sensitive_data(id)
