import pytest
from httpx import AsyncClient
from unittest.mock import patch
from core.security.authentication import get_auth_user
from fastapi import FastAPI
from core.constants import BASE_ROUTE

@pytest.mark.asyncio
async def test_get_AI_applications(client: AsyncClient, app: FastAPI):
    app.dependency_overrides[get_auth_user] = test_authorize_mock
    response = await client.get(
        f"{BASE_ROUTE}/ai_applications",
    )
    assert response.status_code == 200
    assert response.json() != {}
    with patch('core.llm_constants.AI_application.get_AI_applications_for_ui') as mock_get_data:
        mock_get_data.return_value = None
        response = await client.get(
            f"{BASE_ROUTE}/ai_applications",
        )
        assert response.status_code == 500


def test_authorize_mock():
    return {
        "user_id": "test",
        "user_name": "test"
    }