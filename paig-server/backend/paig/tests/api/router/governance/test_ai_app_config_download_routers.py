import pytest
from core.security.authentication import get_auth_user
from fastapi import FastAPI
from httpx import AsyncClient
import json

governance_services_base_route = "/governance-service/api/ai"
encryption_router_base_route = "/account-service/api/data-protect"


class TestAIApplicationConfigDownloadRouter:
    def setup_method(self):
        self.ai_application_dict = {
            "id": 1,
            "status": 1,
            "name": "test_app1",
            "description": "test application1",
            "vector_dbs": [],
            "application_key": "app_key"
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_ai_application_config_download_operation(self, client: AsyncClient, app: FastAPI):

        app.dependency_overrides[get_auth_user] = self.auth_user

        app_response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config"
        )

        assert response.status_code == 200


        from api.encryption.events.startup import create_default_encryption_keys
        await create_default_encryption_keys()
        response = await client.post(
            f"{encryption_router_base_route}/keys/generate?key_type=MSG_PROTECT_PLUGIN"
        )

        assert response.status_code == 201

        response = await client.get(
            f"{governance_services_base_route}/application/{app_response.json()['id']}/config/json/download"
        )

        assert response.status_code == 200
        assert response.headers['content-disposition'] == f"attachment;filename=privacera-shield-test_app1-config.json"
        assert response.headers['content-type'] == 'application/json'
        assert response.content is not None
