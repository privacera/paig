import json
import logging
import traceback

from api.shield.logfile.audit_loggers import LocalAuditLogger
from api.shield.model.shield_audit import ShieldAudit
from api.shield.utils import config_utils
from api.shield.logfile.log_message_in_file import LogMessageInFile
from api.shield.utils.custom_exceptions import ShieldException

logger = logging.getLogger(__name__)


class LogMessageInLocal(LogMessageInFile):
    """
      LogMessageInLocal extends LogMessageInFile to log audit messages to the local file system.
      It handles the creation of local audit loggers and the writing of log messages to files.
      """
    def __init__(self):
        """
        Initializes the LogMessageInLocal with directory paths and configuration values.
        """
        super().__init__()
        self.directory_path = config_utils.get_property_value("local_directory_path", "/workdir/shield/audit_logs")
        self.local_audit_logger = None
        self.audit_spool_dir = config_utils.get_property_value("audit_spool_dir", "/workdir/shield/audit-spool")

    async def log(self, log_data: ShieldAudit):
        """
        Logs the audit data to the local file system.

        Args:
            log_data (ShieldAudit): The audit data to log.

        Raises:
            ShieldException: If there is an error writing logs to the local path.
        """
        local_audit_logger = self.get_or_create_local_audit_logger()
        local_audit_logger.log(log_data)

    def write_log_to_local_file(self, full_log_path, log_data):
        """
        Writes the log data to a local file.

        Args:
            full_log_path (str): The full path to the log file.
            log_data (ShieldAudit): The audit data to log.

        Raises:
            ShieldException: If there is an error writing logs to the local path.
        """
        logger.debug(f"Writing logs to local path: {full_log_path}")
        try:
            with open(full_log_path, 'w') as json_file:
                json.dump(log_data.__dict__, json_file)
            logger.debug(f"Logs written to local path: {full_log_path} successfully.")
        except Exception as e:
            logger.error(f"Error writing logs to local path=>{e.__class__}:{e} , Please check whether the user has "
                         f"sufficient permission to write to the path \n{traceback.format_exc()}")
            raise ShieldException(f"Error writing logs to local path=>{e.__class__}:{e}, Please check whether the "
                                  f"user has sufficient permission to write to the path")

    def get_or_create_local_audit_logger(self):
        if self.local_audit_logger is None:
            self.local_audit_logger = LocalAuditLogger(self, self.audit_spool_dir,
                                                       self.max_queue_size,
                                                       self.audit_event_queue_timeout_sec)
            self.local_audit_logger.daemon = True
            self.local_audit_logger.start()
        return self.local_audit_logger
