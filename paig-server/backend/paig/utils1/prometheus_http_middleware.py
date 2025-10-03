from prometheus_client import Counter
from starlette.middleware.base import BaseHTTPMiddleware

# HTTP requests counter
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests processed by PAIG",
    ["method", "path", "status"]
)

class PrometheusHTTPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        # Increment the counter
        http_requests_total.labels(
            method=request.method,
            path=request.url.path,
            status=response.status_code
        ).inc()
        return response

