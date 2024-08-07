from opentelemetry.sdk.resources import Resource
import os


def get_resource():
    """
     Creates and returns an OpenTelemetry `Resource` instance with service-related attributes.
         Returns:
        Resource: An OpenTelemetry `Resource` instance with the specified attributes.
    """
    return Resource.create(
        {
            "service.name": os.environ.get("APP_NAME", "shield"),
            "service.instance.id": os.environ.get("HOSTNAME", "UNKNOWN"),
            "deployment.environment": os.environ.get("GLOBAL_ENV", "UNKNOWN"),
            "service.namespace": os.environ.get("GLOBAL_NAMESPACE", "UNKNOWN")
        }
    )
