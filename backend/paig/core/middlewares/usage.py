import logging
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.utils import format_to_root_path, acquire_lock, snake_to_camel
from apscheduler.triggers.interval import IntervalTrigger
import os
from core import constants
from core.db_session.standalone_session import get_field_counts
from core.factory.metrics_collector import MetricsClient

# set up logging
logger = logging.getLogger(__name__)


# Read interval from environment variable or set a default
INTERVAL_MINUTES = int(os.getenv('INTERVAL_MINUTES', 60 * 24))

scheduler = AsyncIOScheduler()

FIELD_COUNTS = [
    {"table": "user", "field": "username", "alias": "userCount"},
    {"table": "group", "field": "name", "alias": "groupCount"},
    {"table": "ai_application", "field": "name", "alias": "AIAppCount"},
    {"table": "vector_db", "field": "name", "alias": "vectorDbCount"},
    {"table": "ai_application_policy", "field": "id", "alias": "AIPolicyCount"},
    {"table": "vector_db_policy", "field": "id", "alias": "vectorDBPolicyCount"},
]


class CustomExporter(MetricsClient):
    def __init__(self):
        super().__init__()

    async def initialize(self):
        await super().initialize()

    async def export(self):
        return await self.send_post_request()

    async def collect(self):
        for field in FIELD_COUNTS:
            self.data[field["alias"]] = await get_field_counts(field["table"], field["field"])
        all_metrics = self.metric_collector.get_metrics()
        # resetting all metrics
        self.metric_collector.reset_all_counters()
        for key, value in all_metrics.items():
            self.data[snake_to_camel(key)] = value


def register_usage_events(app: FastAPI):
    @app.on_event("startup")
    async def init_usage_collector():
        lock = acquire_lock(format_to_root_path(constants.SCHEDULER_LOCK))
        if lock:
            await exporter.initialize()
            await collect_usage()
            scheduler.start()
            app.state.lock = lock
        else:
            logger.info("Scheduler is already running in another worker.")

    @app.on_event("shutdown")
    async def shutdown_usage_collector():
        if hasattr(app.state, 'lock'):
            scheduler.shutdown()
            app.state.lock.release()
            logger.info("Scheduler shutdown and lock released.")


# Create an instance of the exporter
exporter = CustomExporter()


async def collect_usage():
    await exporter.collect()
    await exporter.export()


# Add job to scheduler with configurable interval
trigger = IntervalTrigger(minutes=INTERVAL_MINUTES)
scheduler.add_job(collect_usage, trigger)