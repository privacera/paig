import logging

from sqlalchemy.exc import IntegrityError
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from api.user.database.db_operations.groups_repository import GroupRepository, GroupMemberRepository
from api.user.database.db_operations.user_repository import UserRepository
from core.exceptions import BadRequestException, NotFoundException
from core.controllers.paginated_response import create_pageable_response
from core.utils import SingletonDepends

logger = logging.getLogger(__name__)


class GroupService:

    def __init__(
            self,
            user_repository: UserRepository = SingletonDepends(UserRepository),
            group_repository: GroupRepository = SingletonDepends(GroupRepository),
            group_member_repository: GroupMemberRepository = SingletonDepends(GroupMemberRepository),
            gov_service_validation_util: GovServiceValidationUtil = SingletonDepends(GovServiceValidationUtil)
    ):
        self.user_repository = user_repository
        self.group_repository = group_repository
        self.group_member_repository = group_member_repository
        self.gov_service_validation_util = gov_service_validation_util

    async def get_all_groups(self):
        return await self.group_repository.get_all_groups()

    async def create_group(self, new_group):
        try:
            updated_group = await self.group_repository.create_group(new_group)
            return updated_group.to_ui_dict()
        except IntegrityError:
            raise BadRequestException(f"Group with name {new_group['name']} already exists")

    async def delete_group(self, group_id=None):
        group = await self.group_repository.get_group(id=group_id)
        if group is None:
            logger.error(f"No group found with given id: {group_id}")
            raise NotFoundException("No group found with given id")

        # Check if group is associated with any AI applications or vector db policies
        await self.gov_service_validation_util.validate_entity_is_not_utilized(group.name, "Group")

        await self.group_repository.delete_group(group)
        return group.to_ui_dict()

    async def update_group(self, group_id, group_params):
        group = await self.group_repository.get_group(id=group_id)
        if group is None:
            logger.error(f"No group found with given id: {group_id}")
            raise NotFoundException("No group found with given id")
        group.description = group_params.description.strip()
        group.status = group_params.status
        updated_group = await self.group_repository.update_group(group)
        return updated_group.to_ui_dict()

    async def update_group_members(self, group_id, group_params):
        usernames_to_add = group_params.addUsers
        usernames_to_delete = group_params.delUsers

        # Check if group exists
        group = await self.group_repository.get_group(id=group_id)
        if group is None:
            logger.error(f"No group found with given id: {group_id}")
            raise NotFoundException("No group found with given id")

        # Query all relevant users in one query
        all_usernames = list(set(usernames_to_add).union(set(usernames_to_delete)))
        if len(all_usernames) == 0:
            return {"message": "No users to add or delete"}

        users = await self.user_repository.get_all_users(filters={"username": all_usernames},
                                                         apply_in_list_filter=True, columns=['id', 'username'])

        if users and len(users) > 0:
            user_dict = {getattr(user, 'username'): user.id for user in users}
        else:
            logger.error(f"No users found with given usernames: {all_usernames}")
            raise NotFoundException("No users found with given usernames")

        # Separate users to add and delete
        user_ids_to_add = {user_dict[username] for username in usernames_to_add if username in user_dict}
        user_ids_to_delete = {user_dict[username] for username in usernames_to_delete if username in user_dict}

        # existing members
        existing_members = await self.group_member_repository.get_group_members(filters={"group_id": group_id},
                                                                                unique=False)
        existing_member_ids = set()
        if existing_members:
            existing_member_ids = {getattr(member, 'user_id') for member in existing_members}

        new_members_to_add = user_ids_to_add - existing_member_ids
        members_to_remove = existing_member_ids & user_ids_to_delete

        if new_members_to_add and len(new_members_to_add) > 0:
            await self.group_member_repository.save_in_bulk(new_members_to_add, group_id)

        if members_to_remove and len(members_to_remove) > 0:
            await self.group_member_repository.delete_in_bulk(group_id, list(members_to_remove))

        return {"message": "Group members updated successfully"}

    async def get_groups_with_members_count(self, search_filters, page, size, sort):
        results, total_count = await self.group_repository.get_groups_with_members_count(search_filters, page, size,
                                                                                         sort)
        contents = [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "createTime": group.create_time,
                "updateTime": group.update_time,
                "usersCount": group.usersCount or 0,
            }
            for group in results
        ]
        return create_pageable_response(contents, total_count, page, size, sort)