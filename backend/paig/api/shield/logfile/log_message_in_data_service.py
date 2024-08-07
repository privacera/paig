from api.audit.api_schemas.access_audit_schema import BaseAccessAuditView
from api.shield.logfile.log_message_in_file import LogMessageInFile
from api.shield.model.shield_audit import ShieldAudit


class LogMessageInDataService(LogMessageInFile):
    """
    This class is responsible for logging messages in the data service. It inherits from the LogMessageInFile class.

    Attributes:
        data_service: An instance of the data service controller's service.
    """

    def __init__(self, data_store_controller):
        """
        Initializes the LogMessageInDataService with a data store controller.

        Args:
            data_store_controller: The controller for the data store service.
        """
        super().__init__()
        self.data_service = data_store_controller.get_service()

    async def log(self, log_data: ShieldAudit):
        """
        Logs the provided data in the data service.

        Args:
            log_data: The data to be logged, an instance of ShieldAudit.

        Returns:
            None
        """
        transformed_audit: BaseAccessAuditView = self.transform_log_audit(log_data)
        await self.data_service.create_access_audit(transformed_audit.dict())

    def transform_log_audit(self, log_data: ShieldAudit) -> BaseAccessAuditView:
        """
        Transforms the provided log data into a BaseAccessAuditView instance.

        Args:
            log_data: The data to be transformed, an instance of ShieldAudit.

        Returns:
            base_access_audit: The transformed data, an instance of BaseAccessAuditView.
        """
        base_access_audit = BaseAccessAuditView()
        base_access_audit.app_key = log_data.applicationKey
        base_access_audit.app_name = log_data.applicationName
        base_access_audit.client_app_key = log_data.clientApplicationKey
        base_access_audit.client_app_name = log_data.clientApplicationName
        base_access_audit.client_host_name = log_data.clientHostname
        base_access_audit.client_ip = log_data.clientIp
        base_access_audit.context = log_data.context
        base_access_audit.event_id = log_data.eventId
        base_access_audit.masked_traits = log_data.maskedTraits
        base_access_audit.messages = log_data.messages
        base_access_audit.number_of_tokens = log_data.numberOfTokens
        base_access_audit.paig_policy_ids = log_data.paigPolicyIds
        base_access_audit.request_id = log_data.requestId
        base_access_audit.request_type = log_data.requestType
        base_access_audit.result = log_data.result
        base_access_audit.tenant_id = log_data.tenantId
        base_access_audit.thread_id = log_data.threadId
        base_access_audit.thread_sequence_number = log_data.threadSequenceNumber
        base_access_audit.traits = log_data.traits
        base_access_audit.user_id = log_data.userId
        base_access_audit.encryption_key_id = log_data.encryptionKeyId
        base_access_audit.event_time = log_data.eventTime
        return base_access_audit
