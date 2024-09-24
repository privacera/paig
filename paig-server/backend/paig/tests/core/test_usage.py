import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, Mock

from core.middlewares.usage import CustomExporter, register_usage_events
from core.factory.metrics_collector import get_metric_client


metric_client = get_metric_client()


@pytest.fixture
def app():
    app = FastAPI()
    register_usage_events(app)
    return app

@pytest.fixture
def client(app):
    return AsyncClient(app=app, base_url="http://test")

@pytest.fixture
def mock_get_field_counts():
    with patch('core.db_session.standalone_session.get_field_counts', new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
def mock_httpx_post():
    with patch('core.factory.posthog.PostHogClient.capture', new_callable=Mock) as mock:
        yield mock

@pytest.fixture
def mock_get_tenant_uuid():
    with patch('core.factory.metrics_collector.get_tenant_uuid', new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_scheduler():
    with patch('apscheduler.schedulers.asyncio.AsyncIOScheduler.start') as mock_start, \
         patch('apscheduler.schedulers.asyncio.AsyncIOScheduler.shutdown') as mock_shutdown, \
         patch('apscheduler.schedulers.asyncio.AsyncIOScheduler.add_job') as mock_add_job:
        yield mock_start, mock_shutdown, mock_add_job

@pytest.mark.asyncio
async def test_export_success(mock_httpx_post, mock_get_tenant_uuid):
    mock_httpx_post.return_value = True
    mock_get_tenant_uuid.return_value = "123"
    exporter = CustomExporter()
    await exporter.initialize(metric_client)
    success = await exporter.export()
    assert success is True

@pytest.mark.asyncio
async def test_export_failure(mock_httpx_post, mock_get_tenant_uuid):
    mock_httpx_post.return_value = False
    mock_get_tenant_uuid.return_value = "123"
    exporter = CustomExporter()
    await exporter.initialize(metric_client)
    success = await exporter.export()
    assert success is False

@pytest.mark.asyncio
async def test_collect(mock_get_field_counts, mock_get_tenant_uuid):
    mock_get_field_counts.return_value = [{"count": 10}]
    mock_get_tenant_uuid.return_value = "123"
    exporter = CustomExporter()
    await exporter.initialize(metric_client)
    await exporter.collect()
    assert "user_count" in exporter.data
    assert "ai_app_count" in exporter.data

