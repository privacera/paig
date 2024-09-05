import pytest
from api.user.controllers.user_controller import UserController
from api.user.database.db_operations.groups_repository import GroupRepository, GroupMemberRepository
from api.user.database.db_operations.user_repository import UserRepository
from faker import Faker

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


class TestUserController:
    @pytest.fixture()
    def test1_user_dict(self):
        return {
            "status": 1,
            "username": "test1",
            "first_name": "TestFirst",
            "last_name": "TestLast",
            "email": "test1@test.com",
            "password": "testpassword1",
            "roles": ["OWNER"]
        }

    @pytest.fixture()
    def test2_user_dict(self):
        return {
            "status": 1,
            "username": "test2",
            "first_name": "TestFirst",
            "last_name": "TestLast",
            "email": "test2@test.com",
            "password": "testpassword2",
            "roles": ["USER"]
        }

    @pytest.fixture
    def user_controller(self, db_session, set_context_session):
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
        user_service = UserService(user_repository=user_repo_mock, group_repository=group_repo_mock,
                                   gov_service_validation_util=gov_service_validation_util)
        group_service = GroupService(user_repository=user_repo_mock, group_repository=group_repo_mock,
                                     group_member_repository=group_member_repo_mock,
                                     gov_service_validation_util=gov_service_validation_util)
        return UserController(user_service, group_service)

    @pytest.mark.asyncio
    async def test_login_user(self, user_controller, test1_user_dict):
        user = await user_controller.create_user(test1_user_dict)
        assert user["username"] == "test1"
        response = await user_controller.login_user({"username": "test1", "password": "testpassword1"})
        assert response.status_code == 303

    @pytest.mark.asyncio
    async def test_login_user_exceptions_with_wrong_password(self, user_controller, test1_user_dict):
        await user_controller.create_user(test1_user_dict)
        with pytest.raises(Exception) as e:
            await user_controller.login_user({"username": "test1", "password": "invalid_pass"})
        assert str(e.value) != None

    @pytest.mark.asyncio
    async def test_create_user(self, user_controller, test2_user_dict):
        user = await user_controller.create_user(test2_user_dict)
        assert user["username"] == "test2"
        # user already exist
        with pytest.raises(Exception) as e:
            await user_controller.create_user(test2_user_dict)
        assert str(e.value) is not None

    @pytest.mark.asyncio
    async def test_create_user_exceptions_with_empty_username(self, user_controller):
        user_dict = {
            "username": "",
        }
        with pytest.raises(Exception) as e:
            await user_controller.create_user(user_dict)
        assert str(e.value) is not None

    @pytest.mark.asyncio
    async def test_get_user(self, user_controller, test1_user_dict):
        user = await user_controller.create_user(test1_user_dict)
        assert user["username"] == "test1"
        user = await user_controller.get_user_info(username="test1")
        assert user.username == "test1"
        user = await user_controller.get_user_info(username="invalid_user", id=fake.random_int())
        assert user is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, user_controller, test1_user_dict, test2_user_dict):
        user = await user_controller.create_user(test1_user_dict)
        assert user["username"] == "test1"
        user = await user_controller.create_user(test2_user_dict)
        assert user["username"] == "test2"
        users = await user_controller.get_all_users()
        assert len(users) == 2
        assert users[0].username == "test1"
        assert users[1].username == "test2"

    @pytest.mark.asyncio
    async def test_update_user(self, user_controller, test1_user_dict):
        user_update_dict = {
            "status": 0,
            "first_name": "FirstUpdated",
            "last_name": "LastUpdated",
            "password": "testpassword2",
            "roles": ["USER"]

        }
        user = await user_controller.create_user(test1_user_dict)
        assert user['username'] == "test1"
        user = await user_controller.get_user_info(username="test1")
        assert user.username == "test1"
        user_dict = {
            "id": user.id,
            "username": user.username,
            "roles": ["OWNER"] if user.is_tenant_owner else ["USER"],
            "email": user.email
        }
        user = await user_controller.update_user(user.id, user_dict, user_update_dict)
        assert user["firstName"] == "FirstUpdated"
        assert user["lastName"] == "LastUpdated"

        with pytest.raises(Exception) as e:
            await user_controller.update_user(user, user_dict, {"username": "test2"})
        assert str(e.value) is not None

    @pytest.mark.asyncio
    async def test_update_user_exceptions_with_email_already_exists(self, user_controller, test1_user_dict, test2_user_dict):
        user = await user_controller.create_user(test1_user_dict)
        assert user["username"] == "test1"
        user = await user_controller.create_user(test2_user_dict)
        assert user["username"] == "test2"
        user = await user_controller.get_user_info(username="test1")
        user_dict = {
            "id": user.id,
            "username": user.username,
            "roles": ["OWNER"] if user.is_tenant_owner else ["USER"],
            "email": user.email
        }
        with pytest.raises(Exception) as e:
            await user_controller.update_user(user.id, user_dict, {"email": "test2@test.com"})
        assert str(e.value) == 'User with email test2@test.com already exists'

    @pytest.mark.asyncio
    async def test_delete_user(self, user_controller, test1_user_dict, test2_user_dict):
        user = await user_controller.create_user(test1_user_dict)
        assert user["username"] == "test1"
        user = await user_controller.get_user_info(username="test1")
        assert user.username == "test1"
        user_dict = {
            "id": user.id,
            "username": user.username,
            "roles": ["OWNER"] if user.is_tenant_owner else ["USER"],
            "email": user.email
        }
        user = await user_controller.create_user(test2_user_dict)
        assert user["username"] == "test2"
        user2 = await user_controller.get_user_info(username="test2")
        assert user2.username == "test2"
        response = await user_controller.delete_user(user2.id, user_dict)
        assert response["username"] == "test2"
        user2 = await user_controller.get_user_info(username="test2")
        assert user2 is None
        with pytest.raises(Exception) as e:
            await user_controller.delete_user(user2.id, user_dict)
        assert str(e.value) is not None
