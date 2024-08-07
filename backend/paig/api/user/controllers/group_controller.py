import logging

logger = logging.getLogger(__name__)


class GroupController:
    def __init__(
            self,
            user_service,
            group_service
    ):
        self.user_service = user_service
        self.group_service = group_service

    async def get_all_groups(self):
        return await self.group_service.get_all_groups()

    async def create_group(self, group_params):
        new_group = dict()
        new_group['description'] = group_params.description.strip()
        new_group['name'] = group_params.name.strip()
        return await self.group_service.create_group(new_group)

    async def delete_group(self, group_id):
        return await self.group_service.delete_group(group_id)

    async def update_group(self, group_id, group_params):
        return await self.group_service.update_group(group_id, group_params)

    async def update_group_members(self, group_id, group_params):
        return await self.group_service.update_group_members(group_id, group_params)

    async def get_groups_with_members_count(self, search_filters, page, size, sort):
        return await self.group_service.get_groups_with_members_count(search_filters, page, size, sort)
