import asyncio
import logging
import threading

from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.utils import format_to_root_path, acquire_lock
from apscheduler.triggers.interval import IntervalTrigger
import os
from core import constants
from core.db_session.standalone_session import get_field_counts, get_counts_group_by
from core.factory.metrics_collector import MetricsClient, get_metric_client
from contextlib import asynccontextmanager
from api.shield.services.application_manager_service import ApplicationManager
from core.factory.events import ScheduledEvent
from core.factory.posthog import get_post_hog_client

# set up logging
logger = logging.getLogger(__name__)


# Read interval from environment variable or set a default
INTERVAL_MINUTES = int(os.getenv('INTERVAL_MINUTES', 60 * 24))

scheduler = AsyncIOScheduler()

FIELD_COUNTS = [
    {"table": "user", "field": "username", "alias": "user_count"},
    {"table": "group", "field": "name", "alias": "group_count"},
    {"table": "ai_application", "field": "name", "alias": "ai_app_count"},
    {"table": "vector_db", "field": "name", "alias": "vector_db_count"},
    {"table": "ai_application_policy", "field": "id", "alias": "ai_policy_count"},
    {"table": "vector_db_policy", "field": "id", "alias": "vector_db_policy_count"},
]


class CustomExporter:
    def __init__(self):
        self.metric_client = None
        self.data = {}
        self.posthog_client = None

    async def initialize(self, metric_client: MetricsClient):
        self.metric_client = metric_client
        self.posthog_client = get_post_hog_client()

    async def export(self):
        event = ScheduledEvent(data=self.data)
        return self.posthog_client.capture(event=event)

    async def collect(self):
        for field in FIELD_COUNTS:
            self.data[field["alias"]] = await get_field_counts(field["table"], field["field"])
        # Get vector db counts
        vector_db_counts = await get_counts_group_by("vector_db", "type")
        for count in vector_db_counts:
            self.data[(count[0] + '_vector_db').lower()] = count[1]
        all_metrics = self.metric_client.metric_collector.get_metrics()
        # resetting all metrics
        self.metric_client.metric_collector.reset_all_counters()
        for key, value in all_metrics.items():
            self.data[key] = value


def threaded_load_scanners():
    logger.info("Starting load scanners in a thread..")
    app_manager = ApplicationManager()
    app_manager.load_scanners("application_key")
    logger.info("Load scanners completed.")


async def background_init_load_scanners():
    """
    Run init_load_scanners as a background task without blocking the main thread.
    """
    logger.info("Scheduling load scanners in a separate thread...")
    # Running the blocking function in the background using asyncio.to_thread
    asyncio.create_task(asyncio.to_thread(threaded_load_scanners))  # Run the blocking code in a background thread


@asynccontextmanager
async def register_usage_events(application: FastAPI):
    async def init_usage_collector():
        metric_client = get_metric_client()
        await metric_client.initialize()
        lock = acquire_lock(format_to_root_path(constants.SCHEDULER_LOCK))
        if lock:
            await background_init_load_scanners()
            await exporter.initialize(metric_client)
            await collect_usage()
            scheduler.start()
            application.state.lock = lock
        else:
            logger.info("Scheduler is already running in another worker.")

    async def shutdown_usage_collector():
        if hasattr(application.state, 'lock'):
            scheduler.shutdown()
            try:
                application.state.lock.release()
            except threading.ThreadError:
                pass
            except Exception as e:
                pass
            logger.info("Scheduler shutdown and lock released.")

    await init_usage_collector()  # called on startup
    yield
    await shutdown_usage_collector()  # called on shutdown


def capture_event_on_action(event):
    return posthog_client.capture(event=event)


async def background_capture_event(event):
    asyncio.create_task(asyncio.to_thread(capture_event_on_action, event))



# Create an instance of the exporter
exporter = CustomExporter()

# Create an instance of the posthog client
posthog_client = get_post_hog_client()


async def collect_usage():
    await exporter.collect()
    await exporter.export()


# Add job to scheduler with configurable interval
trigger = IntervalTrigger(minutes=INTERVAL_MINUTES)
scheduler.add_job(collect_usage, trigger)
