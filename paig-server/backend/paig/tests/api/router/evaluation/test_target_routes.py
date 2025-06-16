import pytest
from httpx import AsyncClient
from core.middlewares.request_session_context_middleware import get_user
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
        app.dependency_overrides[get_user] = self.auth_user
        post_data = {
            "url": "http://localhost:8080",
            "body": {},
            "headers": {},
            "method": "POST",
            "transformResponse": "string",
            "name": "string",
            "ai_application_id": 0,
            "username": "test"
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
            "name": "updated_string",
            "username": "updated_user"
        }
        put_response = await client.put(f"/{evaluation_services_base_route}/target/application/{app_id}",
                                        json=update_data)
        assert put_response.status_code == 200
        updated_app = put_response.json()
        assert updated_app["url"] == "http://localhost1:8080"
        assert updated_app["name"] == "updated_string"
        assert updated_app["username"] == "updated_user"

        # Delete application
        delete_response = await client.delete(f"/{evaluation_services_base_route}/target/application/{app_id}")
        assert delete_response.status_code == 200

        # Verify deletion
        get_deleted_response = await client.get(f"/{evaluation_services_base_route}/target/application/{app_id}")
        assert get_deleted_response.status_code == 404


    @pytest.mark.asyncio
    async def test_check_target_application_connection_success(self, client: AsyncClient, app: FastAPI):
        """Test successful connection to target application"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:8080",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data"}
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
        assert "message" in result
        assert "status_code" in result

    @pytest.mark.asyncio
    async def test_check_target_application_connection_invalid_url(self, client: AsyncClient, app: FastAPI):
        """Test connection with invalid URL"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "invalid-url",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data"}
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 200  # Note: Returns 200 with error in body
        result = response.json()
        assert result["status"] == "error"
        assert "Invalid URL format" in result["message"]
        assert result["status_code"] == 400

    @pytest.mark.asyncio
    async def test_check_target_application_connection_invalid_headers(self, client: AsyncClient, app: FastAPI):
        """Test connection with invalid headers format"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:8080",
            "method": "POST",
            "headers": "invalid-headers",  # Should be a dict
            "body": {"test": "data"}
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 200  # Note: Returns 200 with error in body
        result = response.json()
        assert result["status"] == "error"
        assert "Invalid headers format" in result["message"]
        assert result["status_code"] == 400

    @pytest.mark.asyncio
    async def test_check_target_application_connection_invalid_body(self, client: AsyncClient, app: FastAPI):
        """Test connection with invalid body format"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:8080",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": "invalid-body"  # Should be a dict
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 200  # Note: Returns 200 with error in body
        result = response.json()
        assert result["status"] == "error"
        assert "Invalid body format" in result["message"]
        assert result["status_code"] == 400
