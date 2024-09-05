import os

from opentelemetry.sdk.resources import Resource
from api.shield.otel import otel_utils


def test_get_resource():
    os.environ["APP_NAME"] = "test-app"
    os.environ["HOSTNAME"] = "test-hostname"
    os.environ["GLOBAL_ENV"] = "test-env"
    os.environ["GLOBAL_NAMESPACE"] = "test-namespace"

    expected_resource = Resource.create(
        {
            "service.name": "test-app",
            "service.instance.id": "test-hostname",
            "deployment.environment": "test-env",
            "service.namespace": "test-namespace"
        }
    )

    actual_resource = otel_utils.get_resource()
    assert actual_resource == expected_resource


