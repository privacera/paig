from typing import Any, Generator
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def app() -> Generator[FastAPI, Any, None]:
    from server import create_app
    app = create_app()

    yield app


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI, db_session) -> AsyncClient:
    """
    Create a new FastAPI AsyncClient
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
