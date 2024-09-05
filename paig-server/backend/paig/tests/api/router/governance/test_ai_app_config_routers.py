import json

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.security.authentication import get_auth_user

governance_services_base_route = "governance-service/api/ai"


class TestAIApplicationConfigRouters:
    def setup_method(self):
        self.ai_application_dict = {
            "id": 1,
            "status": 1,
            "name": "test_app1",
            "description": "test application1",
            "vector_dbs": []
        }
        self.ai_application_config_dict = {
            "id": 1,
            "status": 1,
            "allowedUsers": [],
            "allowedGroups": ["public"],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "applicationId": 1
        }
        self.invalid_ai_application_config_dict = {
            "id": 2,
            "status": 1,
            "allowedUsers": ["invalid_user"],
            "allowedGroups": [],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "applicationId": 1
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_ai_application_config_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        app_response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config"
        )
        assert response.status_code == 200
        assert response.json()['allowedGroups'] == ['public']

        update_req = {
            "status": 1,
            "allowedUsers": [],
            "allowedGroups": [],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": []
        }
        response = await client.put(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config",
            content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['allowedGroups'] == []

        response = await client.get(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config"
        )
        assert response.json()['allowedGroups'] == []
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_ai_application_config_crud_negative_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        app_response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config"
        )
        assert response.json()['allowedGroups'] == ['public']
        assert response.status_code == 200

        response = await client.get(
            f"{governance_services_base_route}/application/2/config"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'AI Application not found with ID: [2]'

        update_req = {
            "status": 1,
            "allowedUsers": [],
            "allowedGroups": [],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": []
        }
        response = await client.put(
            f"{governance_services_base_route}/application/2/config", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'AI Application not found with ID: [2]'

        response = await client.put(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config",
            content=json.dumps(self.invalid_ai_application_config_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "User not found with usernames: ['invalid_user']"

        self.invalid_ai_application_config_dict['allowedUsers'] = []
        self.invalid_ai_application_config_dict['deniedUsers'] = ['invalid_user']

        response = await client.put(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config",
            content=json.dumps(self.invalid_ai_application_config_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "User not found with usernames: ['invalid_user']"

        self.invalid_ai_application_config_dict['allowedGroups'] = ["invalid_group"]
        self.invalid_ai_application_config_dict['deniedUsers'] = []

        response = await client.put(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config",
            content=json.dumps(self.invalid_ai_application_config_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Group not found with names: ['invalid_group']"

        self.invalid_ai_application_config_dict['allowedGroups'] = []
        self.invalid_ai_application_config_dict['deniedGroups'] = ["invalid_group"]

        response = await client.put(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config",
            content=json.dumps(self.invalid_ai_application_config_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Group not found with names: ['invalid_group']"
