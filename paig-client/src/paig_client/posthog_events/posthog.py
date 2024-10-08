import posthog
import logging
from .events import ProductTelemetryEvent, PaigClientSetupEvent
from importlib.metadata import version
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
        return cls._instance

    def capture(self, event: ProductTelemetryEvent) -> None:
        self._direct_capture(event)

    def _direct_capture(self, event: ProductTelemetryEvent) -> None:
        try:
            if os.environ.get('PAIG_CLIENT_DEPLOYMENT', 'dev') != "test":
                posthog.capture(
                    event.user_id,
                    event.name,
                    event.properties
                )
        except:
            pass


posthog_client = PostHogClient()


def capture_event(event):
    posthog_client.capture(event=event)


def get_module_version(module_name):
    try:
        return version(module_name)
    except:
        return None


def get_langchain_dependency_versions():
    langchain_dependencies = dict()
    langchain_version = get_module_version('langchain')
    if langchain_version:
        langchain_dependencies['langchain_version'] = langchain_version
    langchain_community_version = get_module_version('langchain-community')
    if langchain_community_version:
        langchain_dependencies['langchain-community_version'] = langchain_community_version
    langchain_core_version = get_module_version('langchain-core')
    if langchain_core_version:
        langchain_dependencies['langchain-core_version'] = langchain_core_version
    langchain_openai_version = get_module_version('langchain-openai')
    if langchain_openai_version:
        langchain_dependencies['langchain-openai_version'] = langchain_openai_version
    return langchain_dependencies


def get_frameworks_dependencies_versions(frameworks):
    dependencies_versions = dict()
    for framework in frameworks:
        if framework == 'langchain':
            langchain_dependency = get_langchain_dependency_versions()
            if langchain_dependency:
                dependencies_versions.update(langchain_dependency)
        elif framework == 'milvus':
            pymilvus_version = get_module_version('pymilvus')
            if pymilvus_version:
                dependencies_versions['pymilvus_version'] = pymilvus_version
        elif framework == 'opensearch':
            opensearch_py_version = get_module_version('opensearch-py')
            if opensearch_py_version:
                dependencies_versions['opensearch-py_version'] = opensearch_py_version
    return dependencies_versions


def capture_setup_event(frameworks):
    event_data = dict()
    event_data['list_of_frameworks'] = frameworks
    dependencies_versions = get_frameworks_dependencies_versions(frameworks)
    if dependencies_versions:
        event_data.update(dependencies_versions)
    paig_common_version = get_module_version('paig-common')
    if paig_common_version:
        event_data['paig-common_version'] = paig_common_version
    openai_version = get_module_version('openai')
    if openai_version:
        event_data['openai_version'] = openai_version
    capture_event(event=PaigClientSetupEvent(data=event_data))
