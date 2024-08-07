from typing import List

from core.controllers.paginated_response import Pageable
from core.db_session import Transactional, Propagation
from api.governance.api_schemas.tag import TagView, TagFilter
from api.governance.services.tag_service import TagService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from core.utils import SingletonDepends


class TagController:
    """
    Controller class specifically for handling Tag entities.

    Args:
        tag_service (TagService): The service class for handling Tag entities.
    """

    def __init__(self,
                 tag_service: TagService = SingletonDepends(TagService),
                 gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil)):
        self.tag_service = tag_service
        self.gov_service_validation_util = gov_service_validation_util

    async def list_tags(self, filter: TagFilter, page_number: int, size: int,
                        sort: List[str]) -> Pageable:
        """
        List Tag based on the provided filter, pagination, and sorting parameters.

        Args:
            filter (TagFilter): The filter object containing the search parameters.
            page_number (int): The page number to retrieve.
            size (int): The number of records to retrieve per page.
            sort (List[str]): The sorting parameters to apply.

        Returns:
            Pageable: The paginated response containing the list of Tag.
        """
        return await self.tag_service.list_tags(
            filter=filter,
            page_number=page_number,
            size=size,
            sort=sort
        )

    @Transactional(propagation=Propagation.REQUIRED)
    async def create_tag(self, request: TagView) -> TagView:
        """
        Create a new Tag.

        Args:
            request (TagView): The view object representing the Tag to create.

        Returns:
            TagView: The created Tag view object.
        """
        return await self.tag_service.create_tag(request)

    async def get_tag_by_id(self, id: int) -> TagView:
        """
        Retrieve an Tag by its ID.

        Args:
            id (int): The ID of the Tag to retrieve.

        Returns:
            TagView: The Tag view object corresponding to the ID.
        """
        return await self.tag_service.get_tag_by_id(id)

    @Transactional(propagation=Propagation.REQUIRED)
    async def update_tag(self, id: int, request: TagView) -> TagView:
        """
        Update an Tag identified by its ID.

        Args:
            id (int): The ID of the Tag to update.
            request (TagView): The updated view object representing the Tag.

        Returns:
            TagView: The updated Tag view object.
        """
        return await self.tag_service.update_tag(id, request)

    @Transactional(propagation=Propagation.REQUIRED)
    async def delete_tag(self, id: int):
        """
        Delete an Tag by its ID.

        Args:
            id (int): The ID of the Tag to delete.
        """
        tag = await self.get_tag_by_id(id)
        await self.gov_service_validation_util.validate_tag_not_utilized(tag.name)
        await self.tag_service.delete_tag(id)
