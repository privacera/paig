from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.metadata_key import MetadataKeyFilter
from api.governance.api_schemas.metadata_value import MetadataValueFilter, MetadataValueView
from api.governance.services.metadata_value_service import MetadataValueService
from api.governance.services.metadata_key_service import MetadataKeyService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from core.utils import SingletonDepends


class MetadataValueController:
    """
    Controller class specifically for handling Metadata Value entities.

    Args:
        metadata_value_service (MetadataValueService): The service class for handling Metadata Value entities.
    """

    def __init__(self,
                 metadata_value_service: MetadataValueService = SingletonDepends(MetadataValueService),
                 metadata_key_service: MetadataKeyService = SingletonDepends(MetadataKeyService),
                 gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil)):
        self.metadata_value_service = metadata_value_service
        self.metadata_key_service = metadata_key_service
        self.gov_service_validation_util = gov_service_validation_util

    async def list_metadata_values(self, filter: MetadataValueFilter, page_number: int, size: int,
                                   sort: List[str]) -> Pageable:
        """
        List Metadata Values based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (MetadataValueFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of MetaData.
        """
        if filter.metadata_name:
            metadata_filter = MetadataKeyFilter()
            metadata_filter.name = filter.metadata_name
            metadata_page = await self.metadata_key_service.list_metadata(metadata_filter, 0, 1, [])
            if metadata_page.content:
                filter.metadata_id = metadata_page.content[0].id
            else:
                return metadata_page

        result = await self.metadata_value_service.list_metadata_values(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

        metadata_map = {}
        metadata_ids = []

        for metadata_value in result.content:
            metadata_id = metadata_value.metadata_id
            metadata_ids.append(metadata_id)
            if metadata_id in metadata_map:
                metadata_map[metadata_id].append(metadata_value)
            else:
                metadata_map[metadata_id] = [metadata_value]

        metadata_list = await self.metadata_key_service.list_metadata_by_ids(metadata_ids)

        for metadata in metadata_list:
            for metadata_value in metadata_map[metadata.id]:
                metadata_value.metadata_name = metadata.name

        return result

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_metadata_value(self, request: MetadataValueView) -> MetadataValueView:
        """
        Create a new Metadata Value.

        Args:
            request (MetadataValueView): The view object representing the Metadata Value to create.

        Returns:
            MetadataValueView: The created Metadata Value view object.
        """
        metadata = await self.metadata_key_service.get_metadata_by_id(request.metadata_id)
        result = await self.metadata_value_service.create_metadata_values(request)
        result.metadata_name = metadata.name
        return result

    async def get_metadata_value_by_id(self, id: int) -> MetadataValueView:
        """
        Retrieve an Metadata Value by its ID.

        Args:
            id (int): The ID of the Metadata Value to retrieve.

        Returns:
            MetadataValueView: The Metadata Value view object corresponding to the ID.
        """
        result = await self.metadata_value_service.get_metadata_value_by_id(id)
        metadata = await self.metadata_key_service.get_metadata_by_id(result.metadata_id)
        result.metadata_name = metadata.name
        return result

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_metadata_value(self, id: int, request: MetadataValueView) -> MetadataValueView:
        """
        Update an Metadata Value identified by its ID.

        Args:
            id (int): The ID of the Metadata Value to update.
            request (MetadataValueView): The updated view object representing the Metadata Value.

        Returns:
            MetadataValueView: The updated Metadata Value view object.
        """
        metadata = await self.metadata_key_service.get_metadata_by_id(request.metadata_id)
        result = await self.metadata_value_service.update_metadata_value(id, request)
        result.metadata_name = metadata.name
        return result

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_metadata_value(self, id: int):
        """
        Delete an Metadata Value by its ID.

        Args:
            id (int): The ID of the Metadata Value to delete.
        """
        metadata_attr = await self.get_metadata_value_by_id(id)
        await self.gov_service_validation_util.validate_metadata_value_not_utilized(metadata_attr.metadata_name,
                                                                                    metadata_attr.metadata_value)
        await self.metadata_value_service.delete_metadata_value(id)
