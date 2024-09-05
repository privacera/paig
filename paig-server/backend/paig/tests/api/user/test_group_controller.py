import pytest
from api.user.controllers.group_controller import GroupController
from api.user.controllers.user_controller import UserController
from api.user.database.db_operations.user_repository import UserRepository
from api.user.database.db_operations.groups_repository import GroupRepository, GroupMemberRepository
from faker import Faker
from api.user.api_schemas.groups_schema import GroupCreateRequest, GroupMemberUpdateRequest, GetGroupsFilterRequest
from core.exceptions import BadRequestException, NotFoundException
from api.governance.database.db_operations.ai_app_config_repository import AIAppConfigRepository
from api.governance.database.db_operations.ai_app_policy_repository import AIAppPolicyRepository
from api.governance.database.db_operations.vector_db_policy_repository import VectorDBPolicyRepository
from api.governance.services.ai_app_config_service import AIAppConfigService
from api.governance.services.ai_app_policy_service import AIAppPolicyService
from api.governance.services.vector_db_policy_service import VectorDBPolicyService
from api.governance.utils.gov_service_validation_util import GovServiceValidationUtil
from api.user.services.user_service import UserService
from api.user.services.group_service import GroupService

fake = Faker()


class TestGroupController:

    def setup_method(self):
        self.test_group = {
            "name": "test_group",
            "description": "test_description",
            "status": 1
        }

    @pytest.fixture
    def controller(self, db_session, set_context_session):
        user_repo_mock = UserRepository()
        group_repo_mock = GroupRepository()
        group_member_repo_mock = GroupMemberRepository()
        ai_app_config_service = AIAppConfigService(
            ai_app_config_repository=AIAppConfigRepository())
        ai_app_policy_service = AIAppPolicyService(
            ai_app_policy_repository=AIAppPolicyRepository())
        vector_db_policy_service = VectorDBPolicyService(
            vector_db_policy_repository=VectorDBPolicyRepository())
        gov_service_validation_util = GovServiceValidationUtil(ai_app_config_service=ai_app_config_service,
                                                               ai_app_policy_service=ai_app_policy_service,
                                                               vector_db_policy_service=vector_db_policy_service)
        user_service = UserService(
            user_repository=user_repo_mock,
            group_repository=group_repo_mock,
            gov_service_validation_util=gov_service_validation_util
        )
        group_service = GroupService(
            user_repository=user_repo_mock,
            group_repository=group_repo_mock,
            group_member_repository=group_member_repo_mock,
            gov_service_validation_util=gov_service_validation_util
        )
        return GroupController(user_service, group_service)

    @pytest.fixture
    def user_controller(self, db_session):
        user_repo_mock = UserRepository()
        group_repo_mock = GroupRepository()
        group_member_repo_mock = GroupMemberRepository()
        ai_app_config_service = AIAppConfigService(
            ai_app_config_repository=AIAppConfigRepository())
        ai_app_policy_service = AIAppPolicyService(
            ai_app_policy_repository=AIAppPolicyRepository())
        vector_db_policy_service = VectorDBPolicyService(
            vector_db_policy_repository=VectorDBPolicyRepository())
        gov_service_validation_util = GovServiceValidationUtil(ai_app_config_service=ai_app_config_service,
                                                               ai_app_policy_service=ai_app_policy_service,
                                                               vector_db_policy_service=vector_db_policy_service
                                                               )
        user_service = UserService(user_repository=user_repo_mock, group_repository=group_repo_mock,
                                   gov_service_validation_util=gov_service_validation_util)
        group_service = GroupService(user_repository=user_repo_mock, group_repository=group_repo_mock,
                                     group_member_repository=group_member_repo_mock,
                                     gov_service_validation_util=gov_service_validation_util
                                     )
        return UserController(user_service, group_service)

    @pytest.mark.asyncio
    async def test_get_groups(self, controller):
        response = await controller.get_all_groups()
        assert response == []

    @pytest.mark.asyncio
    async def test_group_controller(self, controller):
        test_group_obj = GroupCreateRequest(**self.test_group)
        create_group = await controller.create_group(test_group_obj)
        assert create_group['name'] == 'test_group'
        response = await controller.get_all_groups()
        response = response[0].__dict__
        assert response['name'] == 'test_group'
        with pytest.raises(BadRequestException) as exc_info:
            await controller.create_group(test_group_obj)
        assert len(str(exc_info.value)) > 1

        update_group = await controller.update_group(1, test_group_obj)
        assert update_group['name'] == 'test_group'

        delete_group = await controller.delete_group(1)
        assert delete_group['name'] == 'test_group'



    @pytest.mark.asyncio
    async def test_group_member_controller(self, controller, user_controller):
        test_group_obj = GroupCreateRequest(**self.test_group)
        await controller.create_group(test_group_obj)
        update_group_obj = GroupMemberUpdateRequest(addUsers=["test_user_random"], delUsers=[])
        with pytest.raises(NotFoundException) as exc_info:
            await controller.update_group_members(1, update_group_obj)
        assert len(str(exc_info.value)) > 1
        with pytest.raises(NotFoundException) as exc_info:
            await controller.update_group_members(1000, GroupMemberUpdateRequest(addUsers=[], delUsers=[]))
        assert len(str(exc_info.value)) > 1
        update_group_obj = GroupMemberUpdateRequest(addUsers=[], delUsers=[])
        assert await controller.update_group_members(1, update_group_obj)  is not None

        user_dict = {
            "status": 1,
            "username": "test",
            "first_name": "TestFirst",
            "last_name": "TestLast",
            "email": "test2@test.com",
            "password": "testpassword1",
            "roles": ["OWNER"]
        }
        response = await user_controller.create_user(user_dict)
        assert response is not None

        resp = await controller.update_group_members(1, GroupMemberUpdateRequest(addUsers=['test'], delUsers=[]))
        assert resp is not None

        resp = await controller.update_group_members(1, GroupMemberUpdateRequest(addUsers=[], delUsers=['test']))
        assert resp  is not None

        search_filters = GetGroupsFilterRequest()
        search_filters.name = 'test_group'
        resp = await controller.get_groups_with_members_count(search_filters, 0, 15, ['createTime,desc'])
        assert resp.content is not None
