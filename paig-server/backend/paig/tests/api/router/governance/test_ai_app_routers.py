import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user

governance_services_base_route = "governance-service/api/ai"


class TestAIApplicationRouters:
    def setup_method(self):
        self.ai_application_dict = {
            "id": 1,
            "status": 1,
            "name": "test_app1",
            "description": "test application1",
            "vector_dbs": [],
            "guardrails": []
        }
        self.invalid_ai_application_dict = {
            "id": 2,
            "status": 1,
            "description": "test application1",
            "vector_dbs": []
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_ai_application_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/application"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['name'] == 'test_app1'

        response = await client.get(
            f"{governance_services_base_route}/application/1"
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'test_app1'

        update_req = {
            "status": 1,
            "name": "test_app1_updated",
            "description": "test application1 updated",
            "applicationKey": response.json()['applicationKey'],
            "vector_dbs": []
        }
        response = await client.put(
            f"{governance_services_base_route}/application/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'test_app1_updated'
        assert response.json()['description'] == 'test application1 updated'

        response = await client.delete(
            f"{governance_services_base_route}/application/1"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_ai_application_crud_negative_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/application"
        )
        assert response.json()['content'][0]['name'] == 'test_app1'
        assert response.status_code == 200

        application_key = response.json()['content'][0]['applicationKey']

        response = await client.get(
            f"{governance_services_base_route}/application/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        update_req = {
            "status": 1,
            "name": "test_app1_updated",
            "description": "test application1 updated",
            "applicationKey": application_key,
            "vector_dbs": []
        }
        response = await client.put(
            f"{governance_services_base_route}/application/2", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.delete(
            f"{governance_services_base_route}/application/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.invalid_ai_application_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI Application name must be provided"

        self.invalid_ai_application_dict['name'] = "test_app2"
        self.invalid_ai_application_dict['vector_dbs'] = ["invalid_vector_db"]
        response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.invalid_ai_application_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Vector DB not found with names: ['invalid_vector_db']"

        response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application already exists with name: ['test_app1']"

        response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(update_req)
        )
        assert response.status_code == 201
        update_req_id = response.json()['id']
        self.ai_application_dict['applicationKey'] = response.json()['applicationKey']
        response = await client.put(
            f"{governance_services_base_route}/application/{update_req_id}", content=json.dumps(self.ai_application_dict)
        )
        assert response.status_code == 400
        assert response.json()['message'] == "AI application already exists with name: ['test_app1']"

        self.invalid_ai_application_dict['applicationKey'] = self.ai_application_dict['applicationKey']
        response = await client.put(
            f"{governance_services_base_route}/application/{update_req_id}", content=json.dumps(self.invalid_ai_application_dict)
        )
        assert response.status_code == 400
        assert response.json()['message'] == "Vector DB not found with names: ['invalid_vector_db']"

    @pytest.mark.asyncio
    async def test_ai_application_crud_operations_with_guardrail_details(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        new_ai_app_dict = self.ai_application_dict.copy()
        new_ai_app_dict['guardrailDetails'] = "{\"guardrail_id\": \"guardrail1\",  \"guardrail_version\": \"DRAFT\",\"region\": \"us-east-1\"}"

        await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(new_ai_app_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/application"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['guardrailDetails'] == new_ai_app_dict['guardrailDetails']
        app_id = str(response.json()['content'][0]['id'])

        response = await client.get(
            f"{governance_services_base_route}/application/" + app_id
        )
        assert response.status_code == 200
        assert response.json()['guardrailDetails'] == new_ai_app_dict['guardrailDetails']

        update_req = {
            "status": 1,
            "name": "test_guardrail_app1",
            "description": "test application1 updated",
            "applicationKey": response.json()['applicationKey'],
            "vector_dbs": [],
            "guardrailDetails": "{\"guardrail_id\": \"guardrail2\",  \"guardrail_version\": \"DRAFT\",\"region\": \"us-east-1\"}"
        }
        response = await client.put(
            f"{governance_services_base_route}/application/" + app_id, content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['guardrailDetails'] == "{\"guardrail_id\": \"guardrail2\",  \"guardrail_version\": \"DRAFT\",\"region\": \"us-east-1\"}"

        response = await client.delete(
            f"{governance_services_base_route}/application/" + app_id
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_ai_application_crud_operations_with_guardrails(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        new_ai_app_dict = self.ai_application_dict.copy()
        new_ai_app_dict['guardrails'] = ["guardrail1"]

        await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(new_ai_app_dict)
        )

        response = await client.get(
            f"{governance_services_base_route}/application"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['guardrails'] == ['guardrail1']
        app_id = str(response.json()['content'][0]['id'])

        response = await client.get(
            f"{governance_services_base_route}/application/" + app_id
        )
        assert response.status_code == 200
        assert response.json()['guardrails'] == ['guardrail1']

        update_req = {
            "status": 1,
            "name": "test_guardrail_app1",
            "description": "test application1 updated",
            "applicationKey": response.json()['applicationKey'],
            "vector_dbs": [],
            "guardrails": ["guardrail2"]
        }
        response = await client.put(
            f"{governance_services_base_route}/application/" + app_id, content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['guardrails'] == ['guardrail2']

        response = await client.delete(
            f"{governance_services_base_route}/application/" + app_id
        )
        assert response.status_code == 204
