import copy
import os
import re
import httpx
from core.db_session.standalone_session import get_tenant_uuid
from core.config import get_version

URL_MAPPING = [
    (r"^/shield/authorize/vectordb", "vectordb_authorize_requests"),
    (r"^/shield/authorize", "authorize_requests"),
    (r"^/governance-service/api/", "governance_requests"),
    (r"^/account-service/api/data-protect/decrypt", "audit_details_requests"),
    (r"^/account-service/api/", "user_requests"),
    (r"^/authz-service/api/", "authz_requests"),
    (r"^/data-service/api/shield_audits/", "audit_requests")
]
API_KEY = "227aaf0a-1f4d-4519-af21-fdc854f6acfd"


class HTTPMetricsCollector:
    def __init__(self, metric_collector):
        self.total_requests = "total_requests"
        self.metric_collector = metric_collector

    def capture_http_request(self, path):
        # Increment the HTTP request count
        self.metric_collector.increment_counter(self.total_requests)

        # match pattern and increment the count
        for pattern in URL_MAPPING:
            if re.compile(pattern[0]).match(path):
                self.metric_collector.increment_counter(pattern[1])
                break

    def set_http_request_counter(self, name='total_requests'):
        self.total_requests = name
        self.metric_collector.set_counter(self.total_requests)


class MetricCollector:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricCollector, cls).__new__(cls)
            cls._instance.counters = dict()
            cls._instance.default_counter = dict()
            cls._instance.http_metrics_collector = HTTPMetricsCollector(cls._instance)
        return cls._instance

    def increment_counter(self, name, amount=1):
        if name not in self.counters:
            self.counters[name] = 0
            self.default_counter[name] = 0
        self.counters[name] += amount

    def decrement_counter(self, name, amount=1):
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] -= amount

    def reset_counter(self, name):
        self.counters[name] = 0

    def reset_all_counters(self):
        self.counters = copy.deepcopy(self.default_counter)

    def get_metrics(self, name=None):
        if name:
            return self.counters.get(name, 0)
        return self.counters

    def set_counter(self, name, value=0):
        if name not in self.counters:
            self.default_counter[name] = value
        self.counters[name] = value


class MetricsClient:
    def __init__(self):
        self.data = {}
        self.metric_collector = None
        self.endpoint = str(os.getenv("EXPORTER_ENDPOINT", "http://localhost:8000/usage"))
        self.timeout = 30
        self.headers = {"Authorization": f"Bearer {API_KEY}"}

    async def initialize(self):
        await self._fetch_tenant_uuid()
        self.data['version'] = get_version()
        self.metric_collector = get_metric_collector()

    async def _fetch_tenant_uuid(self):
        self.data["tenantUUID"] = await get_tenant_uuid()

    async def send_post_request(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.endpoint, json=self.data, timeout=self.timeout, headers=self.headers)
                if response.status_code == 200:
                    return True
                return False
        except:
            return False


def get_metric_collector():
    return MetricCollector()
