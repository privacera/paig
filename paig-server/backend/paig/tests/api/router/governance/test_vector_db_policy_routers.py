import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user

governance_services_base_route = "governance-service/api/ai"
user_services_base_route = "account-service/api"


class TestVectorDBPolicyRouters:
    def setup_method(self):
        self.metadata_dict = {
            "id": 1,
            "status": 1,
            "name": "CONFIDENTIAL_METADATA",
            "type": "USER_DEFINED",
            "description": "CONFIDENTIAL_METADATA desc",
            "valueDataType": "multi_value"
        }
        self.metadata_attr_dict = {
            "status": 1,
            "metadataId": 1,
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE"
        }
        self.vector_db_dict = {
            "id": 1,
            "status": 1,
            "name": "test_vector_db1",
            "description": "test vector db1",
            "type": "OPENSEARCH",
            "userEnforcement": 1,
            "groupEnforcement": 1
        }
        self.vector_db_policy_dict = {
            "status": 1,
            "name": "vector_db_policy_1",
            "description": "vector db policy 1",
            "allowedUsers": [],
            "allowedGroups": ["public"],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "metadataKey": "CONFIDENTIAL_METADATA",
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE",
            "operator": "eq"
        }
        self.invalid_vector_db_policy_dict = {
            "status": 1,
            "allowedUsers": [],
            "allowedGroups": ["public"],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "operator": "ne"
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

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.metadata_dict)
        )
        assert response.status_code == 201
        assert response.json()['name'] == 'CONFIDENTIAL_METADATA'

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict)
        )
        assert response.status_code == 201
        assert response.json()['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE'

        response = await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.vector_db_dict)
        )
        assert response.status_code == 201
        vector_db_id = response.json()['id']

        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy", content=json.dumps(self.vector_db_policy_dict)
        )
        assert response.status_code == 201
        assert response.json()['name'] == 'vector_db_policy_1'
        assert response.json()['metadataKey'] == 'CONFIDENTIAL_METADATA'
        assert response.json()['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE'
        assert response.json()['operator'] == 'eq'
        assert response.json()['allowedGroups'] == ['public']

        vector_db_policy_id = response.json()['id']

        response = await client.get(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['name'] == 'vector_db_policy_1'

        response = await client.get(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/{vector_db_policy_id}"
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'vector_db_policy_1'
        assert response.json()['metadataKey'] == 'CONFIDENTIAL_METADATA'
        assert response.json()['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE'

        update_req = {
            "status": 1,
            "name": "vector_db_policy_1_updated",
            "description": "vector db policy 1 updated",
            "allowedUsers": [],
            "allowedGroups": ["public"],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "metadataKey": "CONFIDENTIAL_METADATA",
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE",
            "operator": "eq"
        }
        response = await client.put(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/{vector_db_policy_id}", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'vector_db_policy_1_updated'
        assert response.json()['description'] == 'vector db policy 1 updated'

        response = await client.delete(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/{vector_db_policy_id}"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_vector_db_crud_negative_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.metadata_dict)
        )
        assert response.status_code == 201
        assert response.json()['name'] == 'CONFIDENTIAL_METADATA'

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict)
        )
        assert response.status_code == 201
        assert response.json()['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE'

        response = await client.post(
            f"{governance_services_base_route}/vectordb", content=json.dumps(self.vector_db_dict)
        )
        assert response.status_code == 201
        vector_db_id = response.json()['id']

        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.vector_db_policy_dict)
        )
        assert response.status_code == 201

        response = await client.get(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy"
        )
        assert response.json()['content'][0]['name'] == 'vector_db_policy_1'
        assert response.status_code == 200

        response = await client.get(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Vector DB policy not found with Id: [2]'

        update_req = {
            "status": 1,
            "name": "vector_db_policy_1_updated",
            "description": "vector db policy 1 updated",
            "allowedUsers": [],
            "allowedGroups": ["public"],
            "allowedRoles": [],
            "deniedUsers": [],
            "deniedGroups": [],
            "deniedRoles": [],
            "metadataKey": "CONFIDENTIAL_METADATA",
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE",
            "operator": "eq"
        }
        response = await client.put(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/2", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Vector DB policy not found with Id: [2]'

        response = await client.delete(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Vector DB policy not found with Id: [2]'

        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.invalid_vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Meta data must be provided"

        # Skip this test case as metadata key validation is skipped
        # self.invalid_vector_db_policy_dict['metadataKey'] = "INVALID_METADATA"
        # response = await client.post(
        #     f"{governance_services_base_route}/vectordb/{vector_db_id}/policy", content=json.dumps(self.invalid_vector_db_policy_dict)
        # )
        # assert response.status_code == 400
        # assert response.json()['success'] is False
        # assert response.json()['message'] == "Vector DB policy MetaData not found with key: ['INVALID_METADATA']"

        self.invalid_vector_db_policy_dict['metadataKey'] = "CONFIDENTIAL_METADATA"
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.invalid_vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Meta data value must be provided"

        # Skip this test case as metadata value validation is skipped
        # self.invalid_vector_db_policy_dict['metadataValue'] = "INVALID_METADATA_VALUE"
        # response = await client.post(
        #     f"{governance_services_base_route}/vectordb/{vector_db_id}/policy", content=json.dumps(self.invalid_vector_db_policy_dict)
        # )
        # assert response.status_code == 400
        # assert response.json()['success'] is False
        # assert response.json()['message'] == "Vector DB policy MetaData attribute not found with value: ['INVALID_METADATA_VALUE']"

        self.invalid_vector_db_policy_dict['metadataValue'] = "CONFIDENTIAL_METADATA_VALUE"
        self.invalid_vector_db_policy_dict['allowedUsers'] = ['invalid_user']
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy", content=json.dumps(self.invalid_vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "User not found with usernames: ['invalid_user']"

        self.invalid_vector_db_policy_dict['allowedUsers'] = []
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.invalid_vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Operator value ['ne'] is invalid. Allowed values are: ['eq']"

        self.invalid_vector_db_policy_dict['operator'] = 'eq'
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.invalid_vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Vector DB policy already exists with same meta data key and value: CONFIDENTIAL_METADATA and CONFIDENTIAL_METADATA_VALUE"

        self.invalid_vector_db_policy_dict['allowedGroups'] = []
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.invalid_vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Users, Groups or Roles in Vector DB policy must be provided"

        self.invalid_vector_db_policy_dict['allowedGroups'] = ['public']
        self.invalid_vector_db_policy_dict['deniedGroups'] = ['public']
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(self.invalid_vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Vector DB Policy has Everyone in Granted Access so no other user/group/role can be added in Denied Access"

        self.metadata_attr_dict['metadataValue'] = 'RESTRICTED_METADATA_VALUE'
        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict)
        )
        assert response.status_code == 201
        assert response.json()['metadataValue'] == 'RESTRICTED_METADATA_VALUE'

        update_req['metadataValue'] = 'RESTRICTED_METADATA_VALUE'
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(update_req)
        )
        assert response.status_code == 201
        update_req_id = response.json()['id']

        response = await client.put(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy/{update_req_id}",
            content=json.dumps(self.vector_db_policy_dict)
        )
        assert response.status_code == 400
        assert response.json()['message'] == "Vector DB policy already exists with same meta data key and value: CONFIDENTIAL_METADATA and CONFIDENTIAL_METADATA_VALUE"

        update_req['status'] = 0
        response = await client.post(
            f"{governance_services_base_route}/vectordb/{vector_db_id}/policy",
            content=json.dumps(update_req)
        )
        assert response.status_code == 201
        assert response.json()['status'] == 0
