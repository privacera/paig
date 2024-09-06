import pytest
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user
from fastapi import FastAPI


user_services_base_route = "account-service/api"


class TestUserRouters:
    def setup_method(self):
        self.user = {
          "username": "test_user1",
          "status": 1,
          "firstName": "first_user",
          "lastName": "user_1",
          "password": "password1",
          "roles": ["OWNER"],
          "email": "user1@test.com",
          "groups": []
        }
        self.tenet_user = {
            "username": "admin",
            "status": 1,
            "firstName": "first_user",
            "lastName": "user_1",
            "password": "password1",
            "roles": ["OWNER"],
            "groups": []
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "admin",
            "firstName": "admin",
            "lastName": "user",
            "roles": ["OWNER"],
            "groups": [],
            "status": 1
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_users_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        # Create tenant user
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.tenet_user)
        )
        assert response.status_code == 201
        assert response.json()["username"] == 'admin'

        # Create user
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.user)
        )

        assert response.status_code == 201
        assert response.json()["username"] == 'test_user1'

        # Login User
        user_dict = {
            "username": "test_user1",
            "password": "password1"
        }
        response = await client.post(
            f"{user_services_base_route}/login", content=json.dumps(user_dict)
        )
        assert response.status_code == 303

        # Login user with invalid password
        user_dict = {
            "username": "test_user1",
            "password": "invalid_password_1"
        }
        response = await client.post(
            f"{user_services_base_route}/login", content=json.dumps(user_dict)
        )
        assert response.status_code == 401

        # login user with empty username
        user_dict = {
            "username": "",
            "password": "password1"
        }
        response = await client.post(
            f"{user_services_base_route}/login", content=json.dumps(user_dict)
        )
        assert response.status_code == 400

        # login user with empty password
        user_dict = {
            "username": "test_user1",
            "password": ""
        }
        response = await client.post(
            f"{user_services_base_route}/login", content=json.dumps(user_dict)
        )
        assert response.status_code == 500

        # Get tenant
        response = await client.get(
            f"{user_services_base_route}/users/tenant"
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'admin'


        # Get all users
        response = await client.get(
            f"{user_services_base_route}/users"
        )
        assert response.json()['content'][0]['username'] == 'admin'
        assert response.json()['content'][1]['username'] == 'test_user1'
        assert response.status_code == 200


        # Get user by id
        response = await client.get(
            f"{user_services_base_route}/users/2"
        )
        assert response.json()['username'] == 'test_user1'
        assert response.status_code == 200


        # Update user
        update_req = {
            "status": 1,
            "firstName": "first_user_updated",
            "lastName": "user_1_updated",
            "roles": ["USER"],
            "email": "user1@test.com",
            "groups": []
        }
        response = await client.put(
            f"{user_services_base_route}/users/2", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['firstName'] == 'first_user_updated'
        assert response.json()['lastName'] == 'user_1_updated'

        # Create Test user2
        test_user2_dict = {
            "username": "test_user2",
            "status": 1,
            "firstName": "User2_fistName",
            "lastName": "User2_LastName",
            "password": "TestUser@2",
            "roles": ["OWNER"],
            "email": "user2@test.com",
            "groups": []
        }

        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(test_user2_dict)
        )
        assert response.status_code == 201
        assert response.json()["username"] == 'test_user2'

        # Test update user email
        test_user2_dict['email'] = 'test_user2@test.com'
        response = await client.put(
            f"{user_services_base_route}/users/3", content=json.dumps(test_user2_dict)
        )
        assert response.status_code == 200
        assert response.json()["username"] == 'test_user2'
        assert response.json()["email"] == 'test_user2@test.com'

        # Test conflict to update user email with existing other user email
        update_req = {
            "status": 1,
            "firstName": "User2_firstName_updated",
            "lastName": "User2_lastName_updated",
            "roles": ["OWNER"],
            "email": "user1@test.com"
        }
        response = await client.put(
            f"{user_services_base_route}/users/3", content=json.dumps(update_req)
        )
        assert response.status_code == 409

        # Test conflict to create user with existing username
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(test_user2_dict)
        )

        assert response.status_code == 409

        # Test conflict to create user with existing email
        test_user2_dict['username'] = 'test_user3'
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(test_user2_dict)
        )

        assert response.status_code == 409


        # Delete user
        response = await client.delete(
            f"{user_services_base_route}/users/2"
        )
        assert response.status_code == 200
        assert response.json()['username'] == 'test_user1'

        # Create user with empty last name and without status
        user_obj = {
            "username": "test_user3",
            "firstName": "first_user",
            "lastName": "",
            "password": "testuser@3",
            "roles": ["OWNER"],
            "groups": []
        }
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(user_obj)
        )
        assert response.status_code == 201
        assert response.json()["username"] == 'test_user3'

        # Create user without last name
        user_obj = {
            "username": "test_user4",
            "status": 1,
            "firstName": "first_user",
            "password": "testuser@4",
            "roles": ["OWNER"],
            "groups": []
        }
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(user_obj)
        )
        assert response.status_code == 201
        assert response.json()["username"] == 'test_user4'



class TestUserFirstNameLastNameValidations:
    def setup_method(self):
        self.user = {
          "username": "test_user1",
          "status": 1,
          "firstName": "first_user",
          "lastName": "user_1",
          "password": "",
          "roles": ["USER"],
          "groups": []
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "admin",
            "firstName": "admin",
            "lastName": "user",
            "roles": ["OWNER"],
            "groups": [],
            "status": 1
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_users_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        response = await client.get(
            f"{user_services_base_route}/users"
        )
        assert response.json()['content'] == []
        assert response.status_code == 200

        # created user with first name and last name with underscore
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.user)
        )
        assert response.status_code == 201
        assert response.json()["firstName"] == 'first_user'
        assert response.json()["lastName"] == 'user_1'


        response = await client.get(
            f"{user_services_base_route}/users"
        )
        assert response.json()['content'][0]['username'] == 'test_user1'
        assert response.status_code == 200

        # Update user with first name and last name with dot
        update_req = {
            "status": 1,
            "firstName": "first.name",
            "lastName": "last.1",
            "roles": ["USER"],
            "groups": []
        }
        response = await client.put(
            f"{user_services_base_route}/users/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['firstName'] == 'first.name'
        assert response.json()['lastName'] == "last.1"

        # update user with first name and last name with apostrophe
        update_req = {
            "status": 1,
            "firstName": "first'1",
            "lastName": "last'1",
            "roles": ["USER"],
            "groups": []
        }
        response = await client.put(
            f"{user_services_base_route}/users/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['firstName'] == "first'1"
        assert response.json()['lastName'] == "last'1"

        # Update user with first name and last name with hyphen
        update_req = {
            "status": 1,
            "firstName": "first-1",
            "lastName": "last-1",
            "roles": ["USER"],
            "groups": []
        }
        response = await client.put(
            f"{user_services_base_route}/users/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['firstName'] == "first-1"
        assert response.json()['lastName'] == "last-1"

        # User create with first name and last name with underscore, hyphen, dot and apostrophe characters
        user_obj = {
            "username": "test_user2",
            "status": 1,
            "firstName": "first.-user's-1",
            "lastName": "last.-user's_1",
            "password": "",
            "roles": ["USER"],
            "groups": []
        }
        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(user_obj)
        )
        assert response.status_code == 201
        assert response.json()["firstName"] == "first.-user's-1"
        assert response.json()["lastName"] == "last.-user's_1"
