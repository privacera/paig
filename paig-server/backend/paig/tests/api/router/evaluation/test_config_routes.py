import pytest
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user
from fastapi import FastAPI


evaluation_services_base_route = "eval-service/api"


class TestConfigRouters:
    def setup_method(self):
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
    async def test_config_routes(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user
        post_data = {
            "url": "http://localhost:8080",
            "body": {},
            "headers": {},
            "method": "POST",
            "transformResponse": "string",
            "name": "string",
            "ai_application_id": 0
        }
        # Create application
        post_response = await client.post(f"/{evaluation_services_base_route}/target/application", json=post_data)

        post_data = {
            "purpose": "string",
            "name": "string",
            "categories": ["string"],
            "custom_prompts": ["string"],
            "application_ids": "1"
        }
        # Create config
        post_response = await client.post(f"/{evaluation_services_base_route}/config/save", json=post_data)
        assert post_response.status_code == 200
        created_config = post_response.json()
        config_id = created_config["id"]

        # Get config list
        get_list_response = await client.get(f"/{evaluation_services_base_route}/config/list")
        assert get_list_response.status_code == 200
        json_resp = get_list_response.json()
        assert "content" in json_resp
        assert isinstance(json_resp["content"], list)

        # Update config
        update_data = {
            "purpose": "updated_string",
            "name": "updated_string",
            "categories": ["updated_string"],
            "custom_prompts": ["updated_string"],
            "application_ids": "1"
        }
        put_response = await client.put(f"/{evaluation_services_base_route}/config/{config_id}", json=update_data)
        assert put_response.status_code == 200
        updated_config = put_response.json()
        assert updated_config["purpose"] == "updated_string"
        assert updated_config["name"] == "updated_string"

        # Delete config
        delete_response = await client.delete(f"/{evaluation_services_base_route}/config/{config_id}")
        assert delete_response.status_code == 200