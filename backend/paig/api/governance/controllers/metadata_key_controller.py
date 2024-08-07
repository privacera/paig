from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.metadata_key import MetadataKeyView, MetadataKeyFilter
from api.governance.services.metadata_key_service import MetadataKeyService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from core.utils import SingletonDepends


class MetadataKeyController:
    """
    Controller class specifically for handling MetaData entities.

    Args:
        metadata_service (MetadataKeyService): The service class for handling MetaData entities.
    """

    def __init__(self,
                 metadata_service: MetadataKeyService = SingletonDepends(MetadataKeyService),
                 gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil)):
        self.metadata_service = metadata_service
        self.gov_service_validation_util = gov_service_validation_util

    async def list_metadata(self, filter: MetadataKeyFilter, page_number: int, size: int,
                            sort: List[str]) -> Pageable:
        """
        List MetaData based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (MetadataKeyFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of MetaData.
        """
        return await self.metadata_service.list_metadata(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_metadata(self, request: MetadataKeyView) -> MetadataKeyView:
        """
        Create a new MetaData.

        Args:
            request (MetadataKeyView): The view object representing the MetaData to create.

        Returns:
            MetadataKeyView: The created MetaData view object.
        """
        return await self.metadata_service.create_metadata(request)

    async def get_metadata_by_id(self, id: int) -> MetadataKeyView:
        """
        Retrieve an MetaData by its ID.

        Args:
            id (int): The ID of the MetaData to retrieve.

        Returns:
            MetadataKeyView: The MetaData view object corresponding to the ID.
        """
        return await self.metadata_service.get_metadata_by_id(id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_metadata(self, id: int, request: MetadataKeyView) -> MetadataKeyView:
        """
        Update an MetaData identified by its ID.

        Args:
            id (int): The ID of the MetaData to update.
            request (MetadataKeyView): The updated view object representing the MetaData.

        Returns:
            MetadataKeyView: The updated MetaData view object.
        """
        return await self.metadata_service.update_metadata(id, request)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_metadata(self, id: int):
        """
        Delete an MetaData by its ID.

        Args:
            id (int): The ID of the MetaData to delete.
        """
        meta_data = await self.get_metadata_by_id(id)
        await self.gov_service_validation_util.validate_metadata_is_not_utilized(meta_data.name)
        await self.metadata_service.delete_metadata(id)
