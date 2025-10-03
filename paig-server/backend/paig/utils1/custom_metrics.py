# utils/custom_metrics.py
from prometheus_client import Gauge

# Service-specific custom metrics
users_total_gauge = Gauge(
    "paig_users_total",
    "Total number of users in the system"
)

groups_total_gauge = Gauge(
    "paig_groups_total",
    "Total number of groups in the system"
)

