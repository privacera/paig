import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import json
from core.security.authentication import get_auth_user


user_services_base_route = "account-service/api"


class TestMetaDataValueRouters:
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
        self.metadata_attr_dict_invalid = {
            "status": 1,
            "metadataId": 2,
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE"
        }
        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }

    def auth_user(self):
        return self.auth_user_obj

    @pytest.mark.asyncio
    async def test_metadata_attr_crud_operations(self, client: AsyncClient, app: FastAPI):
        app.dependency_overrides[get_auth_user] = self.auth_user

        await client.post(
            f"{user_services_base_route}/vectordb/metadata/key", content=json.dumps(self.metadata_dict)
        )

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/key"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['name'] == 'CONFIDENTIAL_METADATA'

        await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict)
        )

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/value"
        )
        assert response.status_code == 200
        assert response.json()['content'][0]['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE'

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/value/1"
        )
        assert response.status_code == 200
        assert response.json()['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE'

        update_req = {
              "id": 1,
              "status": 1,
              "metadataId": 1,
              "metadataName": "CONFIDENTIAL_METADATA",
              "metadataValue": "CONFIDENTIAL_METADATA_VALUE_updated"
        }
        response = await client.put(
            f"{user_services_base_route}/vectordb/metadata/value/1", content=json.dumps(update_req)
        )
        assert response.status_code == 200
        assert response.json()['metadataName'] == 'CONFIDENTIAL_METADATA'
        assert response.json()['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE_updated'

        response = await client.delete(
            f"{user_services_base_route}/vectordb/metadata/value/1"
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
        assert response.status_code == 200
        assert response.json()['content'][0]['name'] == 'CONFIDENTIAL_METADATA'

        await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict)
        )

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/value"
        )

        assert response.status_code == 200
        assert response.json()['content'][0]['metadataValue'] == 'CONFIDENTIAL_METADATA_VALUE'

        response = await client.get(
            f"{user_services_base_route}/vectordb/metadata/value/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        update_req = {
            "metadataId": 1,
            "metadataName": "CONFIDENTIAL_METADATA",
            "metadataValue": "CONFIDENTIAL_METADATA_VALUE_updated"
        }
        response = await client.put(
            f"{user_services_base_route}/vectordb/metadata/value/2", content=json.dumps(update_req)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.delete(
            f"{user_services_base_route}/vectordb/metadata/value/2"
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict_invalid)
        )
        assert response.status_code == 404
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Resource not found with id: [2]'

        response = await client.post(
            f"{user_services_base_route}/vectordb/metadata/value", content=json.dumps(self.metadata_attr_dict)
        )
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == "Metadata Attribute already exists with value: ['CONFIDENTIAL_METADATA_VALUE']"



