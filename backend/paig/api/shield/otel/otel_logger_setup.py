import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from api.shield.otel.otel_utils import get_resource
from api.shield.utils import config_utils


class OtelLoggerProviderManager:
    """
    A singleton manager for the OpenTelemetry logger provider.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(OtelLoggerProviderManager, cls).__new__(cls)
            cls._instance._logger_provider = LoggerProvider(resource=get_resource())
            set_logger_provider(cls._instance._logger_provider)
        return cls._instance

    def get_logger_provider(self):
        """
        Returns the OpenTelemetry logger provider instance.

        Returns:
            LoggerProvider: The singleton instance's logger provider.
        """
        return self._logger_provider


def get_otel_logging_handler(logger_provider):
    """
    Creates and returns an OpenTelemetry logging handler configured with an OTLP exporter.

    Args:
        logger_provider (LoggerProvider): The OpenTelemetry logger provider to be used.

    Returns:
        LoggingHandler: An OpenTelemetry logging handler configured with the OTLP exporter.
    """
    otlp_log_exporter_endpoint = config_utils.get_property_value("otel_exporter_endpoint") + "/v1/logs"
    otlp_exporter = OTLPLogExporter(endpoint=otlp_log_exporter_endpoint)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))
    return LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
