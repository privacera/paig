import pytest
from unittest.mock import AsyncMock, patch, call
from core.factory.metrics_collector import (
    HTTPMetricsCollector,
    MetricCollector,
    MetricsClient,
    get_metric_collector
)

# Test HTTPMetricsCollector
def test_http_metrics_collector_capture_http_request():
    metric_collector = MetricCollector()
    http_metrics_collector = HTTPMetricsCollector(metric_collector)

    path = "/shield/authorize/vectordb"
    http_metrics_collector.set_http_request_counter("total_requests")
    http_metrics_collector.capture_http_request(path)
    assert metric_collector.get_metrics("total_requests") == 1
    assert metric_collector.get_metrics("vectordb_authorize_requests") == 1

def test_http_metrics_collector_set_http_request_counter():
    metric_collector = MetricCollector()
    http_metrics_collector = HTTPMetricsCollector(metric_collector)

    http_metrics_collector.set_http_request_counter(name="custom_requests")
    assert http_metrics_collector.total_requests == "custom_requests"

    http_metrics_collector.capture_http_request("/shield/authorize/vectordb")
    assert metric_collector.get_metrics("custom_requests") == 1

# Test MetricCollector
def test_metric_collector_increment_counter():
    metric_collector = MetricCollector()
    metric_collector.increment_counter("test_counter")
    assert metric_collector.get_metrics("test_counter") == 1

def test_metric_collector_decrement_counter():
    metric_collector = MetricCollector()
    metric_collector.increment_counter("test_counter1")
    metric_collector.decrement_counter("test_counter1")
    assert metric_collector.get_metrics("test_counter1") == 0

def test_metric_collector_reset_counter():
    metric_collector = MetricCollector()
    metric_collector.increment_counter("test_counter", amount=5)
    metric_collector.reset_counter("test_counter")
    assert metric_collector.get_metrics("test_counter") == 0

def test_metric_collector_reset_all_counters():
    metric_collector = MetricCollector()
    metric_collector.increment_counter("test_counter1", amount=5)
    metric_collector.increment_counter("test_counter2", amount=10)
    metric_collector.reset_all_counters()
    assert metric_collector.get_metrics("test_counter1") == 0
    assert metric_collector.get_metrics("test_counter2") == 0

# Test MetricsClient
@pytest.mark.asyncio
async def test_metrics_client_initialize():
    with patch("core.factory.metrics_collector.get_tenant_uuid", new_callable=AsyncMock) as mock_get_tenant_uuid, \
         patch("core.factory.metrics_collector.get_version", return_value="1.0.0"):
        mock_get_tenant_uuid.return_value = "123"
        metrics_client = MetricsClient()
        await metrics_client.initialize()
        assert metrics_client.data["installation_id"] == "123"
        assert metrics_client.data["app_version"] == "1.0.0"
        assert metrics_client.metric_collector is not None

def test_get_metric_collector():
    metric_collector1 = get_metric_collector()
    metric_collector2 = get_metric_collector()
    assert metric_collector1 is metric_collector2
