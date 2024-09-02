import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user

user_services_base_route = "account-service/api"


class TestSensitiveDataRouters:
    def setup_method(self):
        self.sensitive_data_dict = {
            "id": 1,
            "status": 1,
            "name": "US_SSN",
            "type": "USER_DEFINED",
            "description": "A US Social Security Number (SSN) with 9 digits",
        }
        self.invalid_sensitive_data_dict = {
            "id": 2,
            "status": 1,
            "name": "US_SSN_2",
            "type": "INVALID_TYPE",
            "description": "US_SSN_2 desc",
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_sensitive_data_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(self.sensitive_data_dict)
        )

        response = await client.get(
            f"{user_services_base_route}/tags"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['name'] == 'US_SSN'

        response = await client.get(
            f"{user_services_base_route}/tags/1"
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'US_SSN'

        update_req = {
            "name": "US_SSN_UPDATED",
            "type": "USER_DEFINED",
            "description": "US_SSN_UPDATED desc",
        }
        response = await client.put(
            f"{user_services_base_route}/tags/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'US_SSN_UPDATED'
        assert response.json()['description'] == 'US_SSN_UPDATED desc'

        response = await client.delete(
            f"{user_services_base_route}/tags/1"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_sensitive_data_crud_negative_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(self.sensitive_data_dict)
        )

        response = await client.get(
            f"{user_services_base_route}/tags"
        )
        assert response.json()['content'][0]['name'] == 'US_SSN'
        assert response.status_code == 200

        response = await client.get(
            f"{user_services_base_route}/tags/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        update_req = {
            "name": "US_SSN_UPDATED",
            "type": "USER_DEFINED",
            "description": "US_SSN_UPDATED desc"
        }
        response = await client.put(
            f"{user_services_base_route}/tags/2", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.delete(
            f"{user_services_base_route}/tags/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(self.invalid_sensitive_data_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Tag Type value ['INVALID_TYPE'] is invalid. Allowed values are: ['USER_DEFINED']"

        response = await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(self.sensitive_data_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Tag already exists with name: ['US_SSN']"

        response = await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(update_req)
        )
        assert response.status_code == 201
        update_req_id = response.json()['id']
        response = await client.put(
            f"{user_services_base_route}/tags/{update_req_id}", content=json.dumps(self.sensitive_data_dict)
        )
        assert response.status_code == 400
        assert response.json()['message'] == "Tag already exists with name: ['US_SSN']"

