import copy
import os
import platform
import re
from core.db_session.standalone_session import get_tenant_uuid
from core.config import get_version
from core.utils import detect_environment

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

    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsClient, cls).__new__(cls)
            cls._instance.data = dict()
            cls._instance.metric_collector = None
        return cls._instance

    async def initialize(self):
        await self._fetch_tenant_uuid()
        self.data['app_version'] = get_version()
        self.metric_collector = get_metric_collector()
        self.data.update(self._get_system_info())

    async def _fetch_tenant_uuid(self):
        self.data["installation_id"] = await get_tenant_uuid()

    @staticmethod
    def _get_system_info():
        return {
            'python_version': platform.python_version(),
            'os': platform.system(),
            'env': detect_environment(),
            'deployment': os.environ.get('PAIG_DEPLOYMENT', 'dev')
        }

    def get_data(self):
        return self.data


def get_metric_collector():
    return MetricCollector()


def get_metric_client():
    return MetricsClient()
