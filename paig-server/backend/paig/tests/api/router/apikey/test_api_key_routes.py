from core.security.authentication import get_auth_user
from datetime import datetime, timedelta, timezone
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from api.encryption.events.startup import create_default_encryption_keys


base_route = "account-service/api"



class TestApiKeyRouter:
    def token_expiry_date(self):
        dt = datetime.now(timezone.utc) + timedelta(days=30)
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


    def setup_method(self):
        self.api_key_dict = {
          "apiKeyName": "Test app api key",
          "description": "Test description",
          "tokenExpiry": self.token_expiry_date(),
          "applicationId": 111,
        }


        self.auth_user_obj = {
            "id": 1,
            "username": "test",
            "roles": ["USER"]
        }


    def auth_user(self):
        return self.auth_user_obj


    @pytest.mark.asyncio
    async def test_api_key_curd_operation(self, client: AsyncClient, app: FastAPI):
        await create_default_encryption_keys()

        app.dependency_overrides[get_auth_user] = self.auth_user

        response = await client.post(
            f"{base_route}/apikey/v2/generate",
            json=self.api_key_dict,
        )

        assert response.status_code == 201
        assert response.json()['apiKeyName'] == self.api_key_dict['apiKeyName']
        assert response.json()['description'] == self.api_key_dict['description']
        assert response.json()['applicationId'] == self.api_key_dict['applicationId']


        # Get the created API key by application ID pass application id in header
        application_id = self.api_key_dict['applicationId']
        response = await client.get(
            f"{base_route}/apikey/application/getKeys",
            headers={"x-app-id": str(application_id)},
            params={
                "page": 0,
                "size": 15,
                "sort": "tokenExpiry,DESC",
                "keyStatus": "ACTIVE,DISABLED,EXPIRED",
                "exactMatch": False
            }
        )

        assert response.status_code == 200
        assert response.json()['content'] is not None
        assert len(response.json()['content']) > 0
        assert response.json()['content'][0]['apiKeyName'] == self.api_key_dict['apiKeyName']

        # Disable the created API key
        api_key_id = response.json()['content'][0]['id']
        response = await client.put(
            f"{base_route}/apikey/disableKey/{api_key_id}"
        )

        assert response.status_code == 200
        assert response.json()['keyStatus'] == "DISABLED"
        assert response.json()['id'] == api_key_id

        # Get the disabled API key by application ID
        response = await client.get(
            f"{base_route}/apikey/application/getKeys",
            headers={"x-app-id": str(application_id)},
            params={
                "page": 0,
                "size": 15,
                "sort": "tokenExpiry,DESC",
                "keyStatus": "ACTIVE,DISABLED,EXPIRED",
                "exactMatch": False
            }
        )

        assert response.status_code == 200
        assert response.json()['content'] is not None
        assert len(response.json()['content']) > 0
        assert response.json()['content'][0]['keyStatus'] == "DISABLED"


        # Delete the disabled API key
        response = await client.delete(
            f"{base_route}/apikey/{api_key_id}"
        )
        assert response.status_code == 200
        assert response.json() == "API Key deleted successfully"
