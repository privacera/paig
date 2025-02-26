import pytest
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user
from fastapi import FastAPI


evaluation_services_base_route = "eval-service/api"


class TestTargetRouters:
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
    async def test_target_routes(self, client: AsyncClient, app: FastAPI):
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
        assert post_response.status_code == 200
        created_app = post_response.json()

        app_id = created_app["id"]

        # Get application list
        response = await client.get(f"/{evaluation_services_base_route}/target/application/list")
        assert response.status_code == 200
        json_resp = response.json()
        assert "content" in json_resp
        assert isinstance(json_resp["content"], list)

        # Get application by ID
        get_response = await client.get(f"/{evaluation_services_base_route}/target/application/{app_id}")
        assert get_response.status_code == 200
        app_data = get_response.json()
        assert app_data["id"] == app_id
        assert "name" in app_data
        assert "url" in app_data
        assert "config" in app_data

        # Update application
        update_data = {
            "url": "http://localhost1:8080",
            "body": {},
            "headers": {},
            "method": "POST",
            "transformResponse": "updated_string",
            "name": "updated_string"
        }
        put_response = await client.put(f"/{evaluation_services_base_route}/target/application/{app_id}",
                                        json=update_data)
        assert put_response.status_code == 200
        updated_app = put_response.json()
        assert updated_app["url"] == "http://localhost1:8080"
        assert updated_app["name"] == "updated_string"

        # Delete application
        delete_response = await client.delete(f"/{evaluation_services_base_route}/target/application/{app_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        get_deleted_response = await client.get(f"/{evaluation_services_base_route}/target/application/{app_id}")
        assert get_deleted_response.status_code == 404
