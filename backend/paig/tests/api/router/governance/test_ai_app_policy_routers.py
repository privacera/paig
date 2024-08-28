import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user

governance_services_base_route = "governance-service/api/ai"
user_services_base_route = "account-service/api"


class TestAIApplicationPolicyRouters:
    def setup_method(self):
        self.sensitive_data_dict = {
            "id": 1,
            "status": 1,
            "name": "US_SSN",
            "type": "USER_DEFINED",
            "description": "A US Social Security Number (SSN) with 9 digits",
        }
        self.ai_application_dict = {
            "id": 1,
            "status": 1,
            "name": "test_app1",
            "description": "test application1",
            "vector_dbs": []
        }
        self.ai_application_policy_dict = {
            "status": 1,
            "name": "test_ssn_policy",
            "description": "test SSN policy",
            "users": [],
            "groups": ["public"],
            "roles": [],
            "tags": [
                "US_SSN"
            ],
            "prompt": "ALLOW",
            "reply": "DENY",
            "enrichedPrompt": "ALLOW"
        }
        self.invalid_ai_application_policy_dict = {
            "status": 1,
            "name": "test_ssn_policy",
            "description": "test SSN policy",
            "users": [],
            "groups": [],
            "roles": [],
            "tags": [
                "INVALID_DATA"
            ],
            "prompt": "INVALID",
            "reply": "INVALID",
            "enrichedPrompt": "INVALID"
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_ai_application_policy_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(self.sensitive_data_dict)
        )
        app_response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )
        assert app_response.status_code == 201
        app_id = app_response.json()['id']

        response = await client.get(
            f"{governance_services_base_route}/application/{app_id}/policy"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['groups'] == ['public']

        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.ai_application_policy_dict)
        )
        assert response.status_code == 200
        assert response.json()['name'] == "test_ssn_policy"
        assert response.json()['description'] == "test SSN policy"
        assert response.json()['tags'] == ["US_SSN"]
        assert response.json()['groups'] == ["public"]
        assert response.json()['prompt'] == "ALLOW"
        assert response.json()['reply'] == "DENY"

        policy_id = response.json()['id']
        update_req = {
            "status": 1,
            "name": "test_ssn_policy_updated",
            "description": "test SSN policy updated",
            "users": [],
            "groups": ["public"],
            "roles": [],
            "tags": [
                "US_SSN"
            ],
            "prompt": "ALLOW",
            "reply": "REDACT",
            "enrichedPrompt": "ALLOW"
        }
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/{policy_id}", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'test_ssn_policy_updated'
        assert response.json()['description'] == 'test SSN policy updated'
        assert response.json()['tags'] == ['US_SSN']
        assert response.json()['prompt'] == "ALLOW"
        assert response.json()['reply'] == "REDACT"

        response = await client.delete(
            f"{governance_services_base_route}/application/{app_id}/policy/{policy_id}"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_ai_application_crud_negative_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(self.sensitive_data_dict)
        )
        app_response = await client.post(
            f"{governance_services_base_route}/application", content=json.dumps(self.ai_application_dict)
        )
        assert app_response.status_code == 201
        app_id = app_response.json()['id']

        response = await client.get(
            f"{governance_services_base_route}/application/{app_id}/policy"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['groups'] == ['public']

        response = await client.get(
            f"{governance_services_base_route}/application/{app_id}/policy/100"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application policy not found with Id: [100]"

        update_req = {
            "status": 1,
            "name": "test_ssn_policy_updated",
            "description": "test SSN policy updated",
            "users": [],
            "groups": ["public"],
            "roles": [],
            "tags": [
                "US_SSN"
            ],
            "prompt": "ALLOW",
            "reply": "DENY",
            "enrichedPrompt": "ALLOW"
        }
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/100", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application policy not found with Id: [100]"

        response = await client.delete(
            f"{governance_services_base_route}/application/{app_id}/policy/100"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application policy not found with Id: [100]"

        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "prompt: Input should be 'ALLOW', 'DENY' or 'REDACT'"

        self.invalid_ai_application_policy_dict['prompt'] = "ALLOW"
        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "reply: Input should be 'ALLOW', 'DENY' or 'REDACT'"

        self.invalid_ai_application_policy_dict['reply'] = "DENY"
        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "enrichedPrompt: Input should be 'ALLOW', 'DENY' or 'REDACT'"

        self.invalid_ai_application_policy_dict['enrichedPrompt'] = "ALLOW"

        # skip this test case as sensitive data validation is skipped
        # response = await client.post(
        #     f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.invalid_ai_application_policy_dict)
        # )
        # assert response.status_code == 400
        # assert response.json()['success'] is False
        # assert response.json()['message'] == "Sensitive Data not found with names: ['INVALID_DATA']"

        self.invalid_ai_application_policy_dict['tags'] = []
        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Tags must be provided"

        self.invalid_ai_application_policy_dict['tags'] = ["US_SSN"]
        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Users, Groups or Roles in AI Application policy must be provided"

        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.ai_application_policy_dict)
        )
        assert response.status_code == 200
        update_req_id = response.json()['id']

        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(self.ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application policy already exists with description: ['test SSN policy']"

        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy", content=json.dumps(update_req)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application policy already exists with tags: ['US_SSN']"

        self.invalid_ai_application_policy_dict['prompt'] = "INVALID"
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/{update_req_id}",
            content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "prompt: Input should be 'ALLOW', 'DENY' or 'REDACT'"

        self.invalid_ai_application_policy_dict['prompt'] = "ALLOW"
        self.invalid_ai_application_policy_dict['reply'] = "INVALID"
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/{update_req_id}",
            content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "reply: Input should be 'ALLOW', 'DENY' or 'REDACT'"

        self.invalid_ai_application_policy_dict['reply'] = "DENY"
        self.invalid_ai_application_policy_dict['enrichedPrompt'] = "INVALID"
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/{update_req_id}",
            content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "enrichedPrompt: Input should be 'ALLOW', 'DENY' or 'REDACT'"

        self.invalid_ai_application_policy_dict['enrichedPrompt'] = "ALLOW"

        # skip this test case as sensitive data validation is skipped
        # self.invalid_ai_application_policy_dict['tags'] = ["INVALID_DATA"]
        # response = await client.put(
        #     f"{governance_services_base_route}/application/{app_id}/policy/{update_req_id}",
        #     content=json.dumps(self.invalid_ai_application_policy_dict)
        # )
        # assert response.status_code == 400
        # assert response.json()['success'] is False
        # assert response.json()['message'] == "Sensitive Data not found with names: ['INVALID_DATA']"

        self.invalid_ai_application_policy_dict['tags'] = ["US_SSN"]
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/{update_req_id}",
            content=json.dumps(self.invalid_ai_application_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Users, Groups or Roles in AI Application policy must be provided"

        self.sensitive_data_dict['tags'] = "EMAIL_ADDRESS"
        self.sensitive_data_dict['description'] = "A valid email address"
        await client.post(
            f"{user_services_base_route}/tags", content=json.dumps(self.sensitive_data_dict)
        )
        update_req['tags'] = ["EMAIL_ADDRESS"]
        response = await client.post(
            f"{governance_services_base_route}/application/{app_id}/policy",
            content=json.dumps(update_req)
        )
        assert response.status_code == 200
        update_req_id = response.json()['id']

        update_req['description'] = "test SSN policy"
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/{update_req_id}",
            content=json.dumps(update_req)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application policy already exists with description: ['test SSN policy']"

        update_req['description'] = "test SSN policy updated"
        update_req['tags'] = ["US_SSN"]
        response = await client.put(
            f"{governance_services_base_route}/application/{app_id}/policy/{update_req_id}",
            content=json.dumps(update_req)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "AI application policy already exists with tags: ['US_SSN']"

