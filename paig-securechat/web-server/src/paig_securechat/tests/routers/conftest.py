from typing import Any, Generator
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from core.factory.controller_initiator import get_session
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI, Any, None]:
    with patch("services.OpenAI_Application.OpenAIClient.get_openai_llm_client") as mock_openai_llm_client:
        mock_openai_llm_client.return_value = MagicMock()
        from app.server import create_app
        app = create_app()

    yield app


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI, db_session) -> AsyncClient:
    """
    Create a new FastAPI AsyncClient
    """

    async def _get_session():
        return db_session

    app.dependency_overrides[get_session] = _get_session

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client



