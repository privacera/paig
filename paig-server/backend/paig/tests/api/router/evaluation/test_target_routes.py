import pytest
from httpx import AsyncClient
from core.middlewares.request_session_context_middleware import get_user
from fastapi import FastAPI
import json


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
    async def test_target_connection_params_validation_success(self, client: AsyncClient, app: FastAPI):
        """Test successful parameter validation for target connection request"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:8080",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data", "prompt": "{{prompt}}"}
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
    async def test_target_connection_params_validation_without_prompt(self, client: AsyncClient, app: FastAPI):
        """Test successful parameter validation without prompt placeholder"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:8080",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data", "message": "Hello world"}
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
    async def test_target_connection_params_validation_invalid_url(self, client: AsyncClient, app: FastAPI):
        """Test parameter validation with invalid URL - should return 400 due to Pydantic validation"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "invalid-url",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data", "prompt": "{{prompt}}"}
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 400
        result = response.json()
        assert "error_code" in result
        assert "message" in result
        assert "success" in result
        assert result["error_code"] == 400
        assert result["success"] == False
        # Check that the error is related to URL validation
        assert "url" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_target_connection_params_validation_invalid_headers(self, client: AsyncClient, app: FastAPI):
        """Test parameter validation with invalid headers format - should return 400 due to Pydantic validation"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:8080",
            "method": "POST",
            "headers": "invalid-headers",  # Should be a dict
            "body": {"test": "data", "prompt": "{{prompt}}"}
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 400
        result = response.json()
        assert "error_code" in result
        assert "message" in result
        assert "success" in result
        assert result["error_code"] == 400
        assert result["success"] == False
        # Check that the error is related to headers validation
        assert "headers" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_target_connection_params_validation_invalid_body(self, client: AsyncClient, app: FastAPI):
        """Test parameter validation with invalid body format - should return 400 due to Pydantic validation"""
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
        assert response.status_code == 400
        result = response.json()
        assert "error_code" in result
        assert "message" in result
        assert "success" in result
        assert result["error_code"] == 400
        assert result["success"] == False
        # Check that the error is related to body validation
        assert "body" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_target_connection_params_validation_missing_required_fields(self, client: AsyncClient, app: FastAPI):
        """Test parameter validation with missing required fields - should return 400 due to Pydantic validation"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data", "prompt": "{{prompt}}"}
            # Missing 'url' field
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 400
        result = response.json()
        assert "error_code" in result
        assert "message" in result
        assert "success" in result
        assert result["error_code"] == 400
        assert result["success"] == False
        # Check that the error is related to missing required field
        assert "url" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_target_connection_params_validation_invalid_method(self, client: AsyncClient, app: FastAPI):
        """Test parameter validation with invalid HTTP method - should return 400 due to Pydantic validation"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:8080",
            "method": "INVALID_METHOD",  # Invalid HTTP method
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data", "prompt": "{{prompt}}"}
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 400
        result = response.json()
        assert "error_code" in result
        assert "message" in result
        assert "success" in result
        assert result["error_code"] == 400
        assert result["success"] == False
        # Check that the error is related to method validation
        assert "method" in result["message"].lower()

    @pytest.mark.asyncio
    async def test_target_connection_actual_connection_timeout(self, client: AsyncClient, app: FastAPI):
        """Test actual connection timeout scenario (this one actually tests the connection)"""
        app.dependency_overrides[get_user] = self.auth_user
        test_data = {
            "url": "http://localhost:9999",  # Non-existent port to force timeout
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "body": {"test": "data", "prompt": "{{prompt}}"}
        }
        response = await client.post(
            f"/{evaluation_services_base_route}/target/application/connection",
            json=test_data
        )
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "error"
        assert "Connection failed" in result["message"]
        assert result["status_code"] in [502, 504]  # Either connection refused or timeout
