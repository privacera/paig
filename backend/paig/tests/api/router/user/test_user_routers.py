import json

from fastapi import FastAPI
from httpx import AsyncClient
import pytest

from core.security.authentication import get_auth_user

governance_services_base_route = "governance-service/api/ai"
user_services_base_route = "account-service/api"


class TestUserDeletionValidations:
    def setup_method(self):
        self.user = {
          "username": "test_user1",
          "status": 1,
          "firstName": "test1",
          "lastName": "user1",
          "password": "",
          "roles": ["USER"],
          "groups": []
        }
        self.sensitive_data_dict = {
            "id": 1,
            "status": 1,
            "name": "US_SSN",
            "type": "USER_DEFINED",
            "description": "A US Social Security Number (SSN) with 9 digits",
        }
        self.ai_application_dict = {
            "id": 1,
            "status": 1,
            "name": "test_app1",
            "description": "test application1",
            "vector_dbs": []
        }
        self.ai_application_policy_dict = {
            "status": 1,
            "name": "test_ssn_policy",
            "description": "test SSN policy",
            "users": ["test_user1"],
            "groups": ["public"],
            "roles": [],
            "tags": [
                "US_SSN"
            ],
            "prompt": "ALLOW",
            "reply": "DENY",
            "enrichedPrompt": "ALLOW"
        }
        self.ai_application_config_dict = {
            "id": 1,
            "status": 1,
            "allowedUsers": ["test_user1"],
            "allowedGroups": ["public"],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "applicationId": 1
        }
        self.metadata_dict = {
            "id": 1,
            "status": 1,
            "name": "CONFIDENTIAL_METADATA",
            "type": "USER_DEFINED",
            "description": "CONFIDENTIAL_METADATA desc",
            "valueDataType": "multi_value"
        }
        self.metadata_attr_dict = {
            "status": 1,
            "metadataId": 1,
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE"
        }
        self.vector_db_dict = {
            "id": 1,
            "status": 1,
            "name": "test_vector_db1",
            "description": "test vector db1",
            "type": "OPENSEARCH",
            "userEnforcement": 1,
            "groupEnforcement": 1
        }
        self.vector_db_policy_dict = {
            "status": 1,
            "name": "vector_db_policy_1",
            "description": "vector db policy 1",
            "allowedUsers": ["test_user1"],
            "allowedGroups": ["public"],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "metadataKey": "CONFIDENTIAL_METADATA",
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE",
            "operator": "eq"
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

        response = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.user)
        )
        assert response.status_code == 201

        response = await client.get(
            f"{user_services_base_route}/users"
        )
        assert response.json()['content'][0]['username'] == 'test_user1'

        update_req = {
            "status": 1,
            "firstName": "firstname",
            "lastName": "lastname",
            "roles": ["USER"],
            "groups": []
        }
        response = await client.put(
            f"{user_services_base_route}/users/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['firstName'] == 'firstname'
        assert response.json()['lastName'] == 'lastname'

    @pytest.mark.asyncio
    async def test_user_deletions_when_still_being_used_in_app_policy(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.auth_user_obj)
        )
        user_resp = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.user)
        )
        assert user_resp.status_code == 201
        user_id = user_resp.json()['id']
        await client.post(
            f"{user_services_base_route}/sensitive-data", content=json.dumps(self.sensitive_data_dict)
        )
        app_response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )
        assert app_response.status_code == 201
        app_id = app_response.json()['id']

        policy_resp = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.ai_application_policy_dict)
        )
        assert policy_resp.status_code == 200
        policy_id = policy_resp.json()['id']

        response = await client.delete(
            f"{user_services_base_route}/users/{user_id}"
        )
        assert response.status_code == 400
        assert response.json()['message'] == "This User is in use by AI Application with Id: [1] and can not be deleted"

        await client.delete(
            f"{governance_services_base_route}/application/{app_id}/policy/{policy_id}"
        )

        response = await client.delete(
            f"{user_services_base_route}/users/{user_id}"
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_user_deletions_when_still_being_used_in_app_config(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.auth_user_obj)
        )
        user_resp = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.user)
        )
        assert user_resp.status_code == 201
        user_id = user_resp.json()['id']
        await client.post(
            f"{user_services_base_route}/sensitive-data", content=json.dumps(self.sensitive_data_dict)
        )
        app_response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )
        assert app_response.status_code == 201
        app_id = app_response.json()['id']

        policy_resp = await client.put(
            f"{governance_services_base_route}/application/{app_id}/config", content=json.dumps(self.ai_application_config_dict)
        )
        assert policy_resp.status_code == 200

        response = await client.delete(
            f"{user_services_base_route}/users/{user_id}"
        )
        assert response.status_code == 400
        assert response.json()['message'] == "This User is in use by AI Application with Id: [1] and can not be deleted"

        self.ai_application_config_dict["allowedUsers"] = []
        await client.put(
            f"{governance_services_base_route}/application/{app_id}/config", content=json.dumps(self.ai_application_config_dict)
        )

        response = await client.delete(
            f"{user_services_base_route}/users/{user_id}"
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_user_deletions_when_still_being_used_in_vector_db_policy(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.auth_user_obj)
        )
        user_resp = await client.post(
            f"{user_services_base_route}/users", content=json.dumps(self.user)
        )
        assert user_resp.status_code == 201
        user_id = user_resp.json()['id']
        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.metadata_dict)
        )
        assert response.status_code == 201

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict)
        )
        assert response.status_code == 201

        response = await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.vector_db_dict)
        )
        assert response.status_code == 201
        vector_db_id = response.json()['id']

        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.vector_db_policy_dict)
        )
        assert response.status_code == 201
        policy_id = response.json()['id']

        response = await client.delete(
            f"{user_services_base_route}/users/{user_id}"
        )
        assert response.status_code == 400
        assert response.json()['message'] == "This User is in use by Vector DB with Id: [1] and can not be deleted"

        await client.delete(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/{policy_id}"
        )

        response = await client.delete(
            f"{user_services_base_route}/users/{user_id}"
        )
        assert response.status_code == 200
