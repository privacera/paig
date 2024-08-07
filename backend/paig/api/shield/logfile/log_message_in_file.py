from abc import abstractmethod
from datetime import datetime

from api.shield.model.shield_audit import ShieldAudit
from api.shield.utils import config_utils
from api.shield.utils.custom_exceptions import ShieldException
from privacera_shield_common.paig_exception import DiskFullException, AuditEventQueueFullException


class LogMessageInFile:
    """
    LogMessageInFile is a base class for logging audit events to a file system.
    It provides methods to create a file structure and handle logging with specific
    configurations for audit failures and event queue timeouts.
    """

    def __init__(self):
        """
        Initializes the LogMessageInFile with configuration values for handling audit failures
        and event queue timeouts.
        """
        self.audit_failure_error_enabled = config_utils.get_property_value_boolean("audit_failure_error_enabled", True)
        self.audit_event_queue_timeout_sec = config_utils.get_property_value_int("audit_event_queue_timeout_sec", 5)
        self.max_queue_size = config_utils.get_property_value_int("max_queue_size", 0)

    def create_file_structure(self, message_data: ShieldAudit) -> str:
        """
        Creates a file structure based on the tenant ID and event time.

        Args:
            message_data (ShieldAudit): The audit data containing tenant ID and event time.

        Returns:
            str: The file path where the log should be stored.
        """
        event_datetime = datetime.fromtimestamp(message_data.eventTime/1000)
        event_time_year = event_datetime.strftime("%Y")
        event_time_month = event_datetime.strftime("%m")
        event_time_day = event_datetime.strftime("%d")

        folder_structure = f'tenant_id={message_data.tenantId}/year={event_time_year}/month={event_time_month}/day={event_time_day}'
        log_file_name = f'{message_data.tenantId}_{event_time_year}_{event_time_month}_{event_time_day}_{message_data.threadId}_{message_data.threadSequenceNumber}.json'

        return f'{folder_structure}/{log_file_name}'

    @abstractmethod
    def log(self, log_data: ShieldAudit):
        """
        Log the audit data. This method must be implemented in child classes.
        """
        raise NotImplementedError("log method must be implemented in child classes")

    async def log_audit_event(self, audit_event: ShieldAudit):
        """
        Log the audit event.

        Args:
            audit_event (ShieldAudit): The audit event to log.
        """
        try:
            await self.log(audit_event)
        except DiskFullException:
            if self.audit_failure_error_enabled is True:
                raise ShieldException("No space left on device. Disk is full. Please increase the disk size or free "
                                      "up some space to push audits successfully.")
        except AuditEventQueueFullException:
            if self.audit_failure_error_enabled is True:
                raise ShieldException("Audit event queue is full.The push rate is too high for the audit "
                                      "spooler to process.")
        except Exception as e:
            raise ShieldException(f"Failed to log audit record! for audit event: {audit_event} get exception: {e}")

