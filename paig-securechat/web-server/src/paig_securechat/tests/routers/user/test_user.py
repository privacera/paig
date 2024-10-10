import pytest
from httpx import AsyncClient
import json
from sqlalchemy.orm.exc import NoResultFound
from unittest.mock import patch
from core.constants import BASE_ROUTE
from routers.user import user
import pandas as pd

@pytest.mark.asyncio
async def test_user_login(client: AsyncClient):
    dic = {
        "user_name": "test1",
    }
    response = await client.post(
        f"{BASE_ROUTE}/user/login",data=json.dumps(dic)
    )
    assert response.json()['user_id'] is not None

    # relogin
    response_again = await client.post(
        f"{BASE_ROUTE}/user/login", data=json.dumps(dic)
    )
    assert response_again.json()['user_id'] == response.json()['user_id']


@pytest.mark.asyncio
async def test_user_login_exceptions(client: AsyncClient):
    dic = {
        "user_name": "test1",
    }
    with patch('core.factory.database_initiator.BaseOperations.get_by', side_effect=Exception("Something went wrong")):
        response_error = await client.post(
            f"{BASE_ROUTE}/user/login", data=json.dumps(dic)
        )
        assert response_error.json()['error_code'] == 500

    with patch('core.factory.database_initiator.BaseOperations.get_by', side_effect=NoResultFound("No result found")):
        response_error = await client.post(
            f"{BASE_ROUTE}/user/login", data=json.dumps(dic)
        )
        assert response_error.json()['user_id'] is not  None


class TestBasicAuth:
    @pytest.mark.asyncio
    async def test_userlogin_with_basic_auth(self, client: AsyncClient):
        existing_basic_auth_enabled = user.basic_auth_enabled
        existing_user_secrets_df = user.user_secrets_df

        user_secrets_data = {
            "Username": ["test_user1", "test_user2"],
            "Secrets": [
                "scrypt:32768:8:1$B1osiT0dJ4VOL7UF$cd0565e50a95df1d600c998307889d83dfd9b80bb7c46a8ed248f53bd919bc767af3c57cd3200d359fe5c324b335f228014cc0bb42dc36c16541137018719077",
                "scrypt:32768:8:1$z4jZZlLeiEQAa0ba$fdbca7aa9d92b3f5cca68d6500e5c27aa1ec208d54c71c83045d2f5ee082baaa6a1347b13ffed77d91f7316f6c679611447a3c3fa8115707cd595d462ec99af1"
            ]
        }

        user.basic_auth_enabled = "true"
        user.user_secrets_df = pd.DataFrame(user_secrets_data)

        user_data = {
            "user_name": "test_user1",
            "password": "user_pass1"
        }
        response = await client.post(
            f"{BASE_ROUTE}/user/login", data=json.dumps(user_data)
        )
        assert response.status_code == 200
        assert response.json()['user_id'] is not None
        assert response.json()['user_name'] == 'test_user1'

        # relogin
        response_again = await client.post(
            f"{BASE_ROUTE}/user/login", data=json.dumps(user_data)
        )
        assert response.status_code == 200
        assert response_again.json()['user_id'] == response.json()['user_id']
        assert response.json()['user_name'] == response.json()['user_name']


        # Login with test_user2
        user_data = {
            "user_name": "test_user2",
            "password": "user_pass2"
        }
        response = await client.post(
            f"{BASE_ROUTE}/user/login", data=json.dumps(user_data)
        )
        assert response.status_code == 200
        assert response.json()['user_id'] is not None
        assert response.json()['user_name'] == 'test_user2'

        # Invalid username and password
        invalid_user = {
            "user_name": "test_user3",
            "password": "invalid_pass"
        }

        response = await client.post(
            f"{BASE_ROUTE}/user/login", data=json.dumps(invalid_user)
        )
        assert response.status_code == 401

        # Update user existing values
        user.basic_auth_enabled = existing_basic_auth_enabled
        user.user_secrets_df = existing_user_secrets_df