import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user

governance_services_base_route = "governance-service/api/ai"


class TestVectorDBRouters:
    def setup_method(self):
        self.vector_db_dict = {
            "id": 1,
            "status": 1,
            "name": "test_vector_db1",
            "description": "test vector db1",
            "type": "OPENSEARCH",
            "userEnforcement": 1,
            "groupEnforcement": 1
        }
        self.ai_application_dict = {
            "id": 1,
            "status": 1,
            "name": "test_app1",
            "description": "test application1",
            "vector_dbs": ["test_vector_db1"]
        }
        self.invalid_vector_db_dict = {
            "id": 2,
            "status": 1,
            "description": "test vector db1",
            "type": "INVALID",
            "userEnforcement": 1,
            "groupEnforcement": 1
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_vector_db_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.vector_db_dict)
        )

        await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/vectordb"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['name'] == 'test_vector_db1'

        response = await client.get(
            f"{governance_services_base_route}/vectordb/1"
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'test_vector_db1'

        update_req = {
            "status": 1,
            "name": "test_vector_db1_updated",
            "description": "test vector db1 updated",
            "type": "MILVUS",
            "userEnforcement": 1,
            "groupEnforcement": 1
        }
        response = await client.put(
            f"{governance_services_base_route}/vectordb/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'test_vector_db1_updated'
        assert response.json()['description'] == 'test vector db1 updated'
        assert response.json()['type'] == 'MILVUS'

        response = await client.delete(
            f"{governance_services_base_route}/vectordb/1"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_vector_db_crud_negative_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.vector_db_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/vectordb"
        )
        assert response.json()['content'][0]['name'] == 'test_vector_db1'
        assert response.status_code == 200

        response = await client.get(
            f"{governance_services_base_route}/vectordb/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        update_req = {
            "status": 1,
            "name": "test_vector_db1_updated",
            "description": "test vector db1 updated",
            "type": "MILVUS",
            "userEnforcement": 1,
            "groupEnforcement": 1
        }
        response = await client.put(
            f"{governance_services_base_route}/vectordb/2", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.delete(
            f"{governance_services_base_route}/vectordb/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.invalid_vector_db_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "type: Input should be 'OPENSEARCH' or 'MILVUS'"

        self.invalid_vector_db_dict['type'] = "OPENSEARCH"
        response = await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.invalid_vector_db_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Vector DB name must be provided"

        self.invalid_vector_db_dict['name'] = "test_vector_db1"
        response = await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.invalid_vector_db_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Vector DB already exists with name: ['test_vector_db1']"

        response = await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(update_req)
        )
        assert response.status_code == 201
        update_req_id = response.json()['id']
        response = await client.put(
            f"{governance_services_base_route}/vectordb/{update_req_id}", content=json.dumps(self.invalid_vector_db_dict)
        )
        assert response.status_code == 400
        assert response.json()['message'] == "Vector DB already exists with name: ['test_vector_db1']"

