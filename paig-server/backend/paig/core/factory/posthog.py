import posthog
import logging
from core.factory.events import ProductTelemetryEvent
import os

logger = logging.getLogger(__name__)


class PostHogClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostHogClient, cls).__new__(cls)
            posthog.project_api_key = 'phc_Xf9IPAksnaN0YB4HwRang5lE5jzZgZpVvMEqz0gKi4E'
            posthog.host = 'https://us.i.posthog.com'
            posthog.debug = False
            cls._instance.user_id = None
        return cls._instance

    def capture(self, event: ProductTelemetryEvent) -> None:
        self._direct_capture(event)

    def _direct_capture(self, event: ProductTelemetryEvent) -> None:
        try:
            if os.environ.get('PAIG_DEPLOYMENT') != "test":
                posthog.capture(
                    event.user_id,
                    event.name,
                    event.properties
                )
        except:
            pass


def get_post_hog_client():
    return PostHogClient()
