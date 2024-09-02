from starlette.middleware.base import BaseHTTPMiddleware
from core.factory.metrics_collector import get_metric_collector

metrics = get_metric_collector()
metrics.http_metrics_collector.set_http_request_counter()


class RequestCounterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        metrics.http_metrics_collector.capture_http_request(request.url.path)
        response = await call_next(request)
        return response
