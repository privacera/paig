
from api.user.api_schemas.groups_schema import GetGroupsFilterRequest
from api.user.api_schemas.user_schema import GetUsersFilterRequest
from api.user.services.user_service import UserService
from api.user.services.group_service import GroupService
from core.exceptions import BadRequestException
from core.exceptions.error_messages_parser import get_error_message, ERROR_RESOURCE_NOT_FOUND
from core.utils import SingletonDepends


class AccServiceValidationUtil:
    def __init__(self,
                 user_service: UserService = SingletonDepends(UserService),
                 group_service: GroupService = SingletonDepends(GroupService),
                 ):
        self.user_service = user_service
        self.group_service = group_service

    async def validate_users_exists(self, users: list[str]):
        """
        Validates users exists in account service

        Args:
            users (list[str]): List of usernames to validate
        """
        users_set = set(users.copy())
        if not users_set:
            return
        user_filter = GetUsersFilterRequest()
        user_filter.username = ",".join(users_set)
        existing_users = set()
        page_number = 0
        page_size = 100
        while True:
            result = await self.user_service.get_users_with_groups(user_filter, page_number, page_size, [])
            existing_users.update(user["username"] for user in result.content)
            if result.last:
                break
            page_number += 1
        # Step 4: Find differences and raise exception if any user is missing
        missing_users = users_set - existing_users
        if missing_users:
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_NOT_FOUND, "User", "usernames", list(missing_users)))

    async def validate_groups_exists(self, groups: list[str]):
        """
        Validates groups exists in account service

        Args:
            groups (list[str]): List of group names to validate
        """
        group_set = set(groups.copy())
        if "public" in group_set:
            group_set.remove("public")
        if not group_set:
            return

        group_filter = GetGroupsFilterRequest()
        group_filter.name = ",".join(group_set)
        existing_groups = set()
        page_number = 0
        page_size = 100
        while True:
            result = await self.group_service.get_groups_with_members_count(group_filter, page_number, page_size, [])
            existing_groups.update(group["name"] for group in result.content)
            if result.last:
                break
            page_number += 1
        # Step 4: Find differences and raise exception if any user is missing
        missing_groups = group_set - existing_groups
        if missing_groups:
            raise BadRequestException(
                get_error_message(ERROR_RESOURCE_NOT_FOUND, "Group", "names", list(missing_groups)))
