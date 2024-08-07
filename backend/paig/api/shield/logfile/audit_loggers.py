import os

from privacera_shield_common.audit_spooler import AuditLogger

from api.shield.client.fluentd_rest_http_client import FluentdRestHttpClient
from api.shield.model.shield_audit import ShieldAudit
import logging

logger = logging.getLogger(__name__)


def create_message_log_path(directory_path):
    os.makedirs(directory_path, exist_ok=True)
    logger.debug(f"log path '{directory_path}' created successfully.")


class FluentdAuditLogger(AuditLogger):
    """
    FluentAuditLogger class for logging audit events to Fluentd.
    """

    def __init__(self, fluentd_rest_http_client: FluentdRestHttpClient, audit_spool_dir: str,
                 max_queue_size: int,
                 audit_event_queue_timeout_sec: int):
        """
        Initializes a FluentdAuditLogger object.

        Args:
            fluentd_rest_http_client (FluentdRestHttpClient): The REST client for Fluentd.
            audit_spool_dir (str): The directory path where spooled audit events are stored.
            max_queue_size (int): The maximum queue size.
            audit_event_queue_timeout_sec (int): The audit event queue timeout in seconds.
        """
        # Setting max_queue_size to 0 to make the queue size infinite
        super().__init__(audit_spool_dir=audit_spool_dir, audit_event_cls=ShieldAudit,
                         max_queue_size=max_queue_size, audit_event_queue_timeout=audit_event_queue_timeout_sec)
        self.fluentd_rest_http_client = fluentd_rest_http_client

    def push_audit_event_to_server(self, audit_event: ShieldAudit):
        """
        Pushes the audit event to the server.

        Args:
            audit_event (T): The audit event to push.
        """
        self.fluentd_rest_http_client.log_message(audit_event.to_payload_dict())


class S3AuditLogger(AuditLogger):
    """
    S3AuditLogger class for logging audit events to S3.
    """

    def __init__(self, log_message_in_s3, audit_spool_dir: str,
                 max_queue_size: int,
                 audit_event_queue_timeout_sec: int):
        """
        Initializes a S3AuditLogger object.

        Args:
            log_message_in_s3 (LogMessageInS3): The S3 logger.
            audit_spool_dir (str): The directory path where spooled audit events are stored.
            full_object_key (str): The full object key.
            max_queue_size (int): The maximum queue size.
            audit_event_queue_timeout_sec (int): The audit event queue timeout in seconds.
        """
        # Setting max_queue_size to 0 to make the queue size infinite
        super().__init__(audit_spool_dir=audit_spool_dir, audit_event_cls=ShieldAudit,
                         max_queue_size=max_queue_size, audit_event_queue_timeout=audit_event_queue_timeout_sec)
        self.log_message_in_s3 = log_message_in_s3

    def push_audit_event_to_server(self, audit_event: ShieldAudit):
        """
        Pushes the audit event to the server.

        Args:
            audit_event (T): The audit event to push.
        """
        object_key = self.log_message_in_s3.create_file_structure(audit_event)
        full_object_key = "/".join(
            [self.log_message_in_s3.bucket_prefix, object_key]) if self.log_message_in_s3.bucket_prefix else object_key
        logger.debug(
            f"Uploading logs to S3 bucket: {self.log_message_in_s3.bucket_name} with object key: {full_object_key}")
        self.log_message_in_s3.write_log_to_s3(full_object_key, audit_event)


class LocalAuditLogger(AuditLogger):
    """
    LocalAuditLogger class for logging
    audit events to local file system.
    """

    def __init__(self, log_message_in_local, audit_spool_dir: str,
                 max_queue_size: int,
                 audit_event_queue_timeout_sec: int):
        """
        Initializes a LocalAuditLogger object.

        Args:
            log_message_in_local (LogMessageInLocal): The local logger.
            audit_spool_dir (str): The directory path where spooled audit events are stored.
            full_log_path (str): The full log path.
            max_queue_size (int): The maximum queue size.
            audit_event_queue_timeout_sec (int): The audit event queue timeout in seconds.
        """
        # Setting max_queue_size to 0 to make the queue size infinite
        super().__init__(audit_spool_dir=audit_spool_dir, audit_event_cls=ShieldAudit,
                         max_queue_size=max_queue_size, audit_event_queue_timeout=audit_event_queue_timeout_sec)
        self.log_message_in_local = log_message_in_local

    def push_audit_event_to_server(self, audit_event: ShieldAudit):
        """
        Pushes the audit event to the server.

        Args:
            audit_event (T): The audit event to push.
        """
        log_file = self.log_message_in_local.create_file_structure(audit_event)
        full_log_path = os.path.join(self.log_message_in_local.directory_path, log_file)
        log_path = os.path.dirname(full_log_path)
        create_message_log_path(log_path)
        self.log_message_in_local.write_log_to_local_file(full_log_path, audit_event)
