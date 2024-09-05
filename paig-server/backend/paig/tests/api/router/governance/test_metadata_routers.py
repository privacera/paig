import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user


user_services_base_route = "account-service/api"


class TestMetaDataRouters:
    def setup_method(self):
        self.metadata_dict = {
          "id": 1,
          "status": 1,
          "name": "CONFIDENTIAL_METADATA",
          "type": "USER_DEFINED",
          "description": "CONFIDENTIAL_METADATA desc",
          "valueDataType": "multi_value"
        }
        self.invalid_metadata_dict = {
            "id": 2,
            "status": 1,
            "name": "CONFIDENTIAL_METADATA_2",
            "type": "SYSTEM_DEFINED",
            "description": "CONFIDENTIAL_METADATA_2 desc",
            "valueDataType": "single_value"
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_metadata_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.metadata_dict)
        )

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/key"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['name'] == 'CONFIDENTIAL_METADATA'

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/key/1"
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'CONFIDENTIAL_METADATA'

        update_req = {
            "name": "CONFIDENTIAL_METADATA_UPDATED",
            "type": "USER_DEFINED",
            "description": "CONFIDENTIAL_METADATA_UPDATED desc",
            "valueDataType": "multi_value"
        }
        response = await client.put(
            f"{user_services_base_route}/vectordb/metadata/key/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['name'] == 'CONFIDENTIAL_METADATA_UPDATED'
        assert response.json()['description'] == 'CONFIDENTIAL_METADATA_UPDATED desc'


        response = await client.delete(
            f"{user_services_base_route}/vectordb/metadata/key/1"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_metadata_crud_negative_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.metadata_dict)
        )

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/key"
        )
        assert response.json()['content'][0]['name'] == 'CONFIDENTIAL_METADATA'
        assert response.status_code == 200

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/key/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        update_req = {
            "name": "CONFIDENTIAL_METADATA_UPDATED",
            "type": "USER_DEFINED",
            "description": "CONFIDENTIAL_METADATA_UPDATED desc",
            "valueDataType": "multi_value"
        }
        response = await client.put(
            f"{user_services_base_route}/vectordb/metadata/key/2", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.delete(
            f"{user_services_base_route}/vectordb/metadata/key/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.invalid_metadata_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == ("Metadata Key Type value ['SYSTEM_DEFINED'] is invalid. Allowed values are: "
                                              "['USER_DEFINED']")

        self.invalid_metadata_dict['type'] = 'USER_DEFINED'
        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.invalid_metadata_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == ("Metadata Key Data Type value ['single_value'] is invalid. Allowed values are"
                                              ": ['multi_value']")

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.metadata_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Metadata Key already exists with name: CONFIDENTIAL_METADATA'



