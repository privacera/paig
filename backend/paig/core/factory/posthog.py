import posthog
import logging

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

    def set_user_id(self, user_id):
        self.user_id = user_id

    def capture_event(self, event_name, properties=None):
        if properties is None:
            properties = {}
        try:
            posthog.capture(self.user_id, event_name, properties)
        except:
            pass


def get_post_hog_client():
    return PostHogClient()