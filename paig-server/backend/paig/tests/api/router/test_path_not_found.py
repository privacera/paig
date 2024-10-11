import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from core.security.authentication import get_auth_user

user_services_base_route = "account-service/api"
governance_services_base_route = "governance-service/api/ai"


class TestPathNotFound:
    def setup_method(self):
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_invalid_path_account_service_api(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        response = await client.post(
            f"{user_services_base_route}/invalid_path"
        )

        assert response.status_code == 404
        assert response.json()['error_code'] == 404
        assert response.json()['message'] == 'Path Not Found'
        assert (response.json()['path'] == f"/{user_services_base_route}/invalid_path")

    @pytest.mark.asyncio
    async def test_invalid_path_governance_service_api(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        response = await client.get(
            f"{governance_services_base_route}/invalid_path"
        )

        assert response.status_code == 404
        assert response.json()['error_code'] == 404
        assert response.json()['message'] == 'Path Not Found'
        assert (response.json()['path'] == f"/{governance_services_base_route}/invalid_path")
