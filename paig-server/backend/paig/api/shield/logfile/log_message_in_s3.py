import json
import traceback

import boto3
import logging

from botocore.credentials import DeferredRefreshableCredentials
from botocore.credentials import create_assume_role_refresher

from api.shield.logfile.audit_loggers import S3AuditLogger
from api.shield.model.shield_audit import ShieldAudit
from api.shield.utils import config_utils
from api.shield.logfile.log_message_in_file import LogMessageInFile
from api.shield.utils.custom_exceptions import ShieldException

logger = logging.getLogger(__name__)


# Assume the IAM role
def assume_role(assume_role_arn, assume_role_session_name):
    """
    Assumes an IAM role and returns a boto3 session with the assumed role credentials.

    Args:
        assume_role_arn (str): The ARN of the role to assume.
        assume_role_session_name (str): The session name for the assumed role.

    Returns:
        boto3.Session: A boto3 session with the assumed role credentials.
    """
    session = boto3.Session()
    params = {"RoleArn": assume_role_arn, "RoleSessionName": assume_role_session_name}
    session._credentials = DeferredRefreshableCredentials(
        refresh_using=create_assume_role_refresher(boto3.client('sts'), params),
        method='sts-assume-role')

    return session


class LogMessageInS3File(LogMessageInFile):
    """
    LogMessageInS3File extends LogMessageInFile to log audit messages to an S3 bucket.
    It handles the creation of S3 clients and the uploading of log messages to S3.
    """
    def __init__(self):
        """
        Initializes the LogMessageInS3File with S3 client and bucket configuration.
        """

        # Configure boto3 logger
        super().__init__()
        boto3_log_level = logging.getLevelName(config_utils.get_property_value("boto3_log_level", "INFO"))
        logging.getLogger('botocore').setLevel(boto3_log_level)

        # init s3 client
        self.s3_client = None
        self.init_s3_client()

        # validate bucket
        self.bucket_name = None
        self.bucket_prefix = None
        self.validate_bucket()

        self.s3_audit_logger = None
        self.audit_spool_dir = config_utils.get_property_value("audit_spool_dir", "/workdir/shield/audit-spool")

    def init_s3_client(self):
        """
        Initializes the S3 client based on the connection mode specified in the configuration.

        Raises:
            ShieldException: If the S3 connection mode is invalid or required credentials are not provided.
        """
        s3_connection_mode = config_utils.get_property_value("s3_connection_mode", None)
        if s3_connection_mode == "keys":
            # this will use the credentials from properties file
            access_key = config_utils.get_property_value("s3_access_key", None)
            secret_key = config_utils.get_property_value("s3_secret_key", None)
            # if region/session token is not provided, it will be passed as none and boto3 will handle it internally.
            region = config_utils.get_property_value("s3_region", None)
            session_token = config_utils.get_property_value("s3_session_token", None)
            if not access_key or not secret_key:
                raise ShieldException("S3 connection mode is set to keys but keys are not provided! Please set this "
                                      "properties s3_access_key and s3_secret_key")

            self.s3_client = boto3.client('s3',
                                          aws_access_key_id=access_key,
                                          aws_secret_access_key=secret_key,
                                          region_name=region,
                                          aws_session_token=session_token)
        elif s3_connection_mode == "iam_role":
            # this will use the iam role from properties file and assume it
            assume_role_arn = config_utils.get_property_value("s3_assume_role_arn", None)
            # Giving default role session name as it is mandatory for boto3 as None type is not allowed.
            assume_role_session_name = config_utils.get_property_value("s3_assume_role_session_name",
                                                                       "privacera_shield_s3_role_session")
            if not assume_role_arn:
                raise ShieldException("S3 connection mode is set to iam_role but s3_assume_role_arn is not provided!")

            session = assume_role(assume_role_arn, assume_role_session_name)
            self.s3_client = session.client('s3')

        elif s3_connection_mode == "default":
            # this will use the default credentials from ec2 instance role
            self.s3_client = boto3.client('s3')
        else:
            raise ShieldException(f"S3 connection mode provided {s3_connection_mode} is invalid!")

    def validate_bucket(self):
        """
        Validates the S3 bucket specified in the configuration.

        Raises:
            ShieldException: If the S3 bucket name is not provided or the bucket does not exist.
        """
        bucket = config_utils.get_property_value("s3_bucket_name", None)

        if not bucket:
            raise ShieldException("S3 bucket name is not provided! Please set this property s3_bucket_name")

        if bucket.endswith("/"):
            bucket = bucket[:-1]

        bucket_components = bucket.split("/")
        if len(bucket_components) > 1:
            self.bucket_name = bucket_components[0]
            self.bucket_prefix = "/".join(bucket_components[1:])
        else:
            self.bucket_name = bucket
            self.bucket_prefix = ""
        # check for bucket exist
        self.s3_client.head_bucket(Bucket=self.bucket_name)

    async def log(self, log_data: ShieldAudit):
        s3_audit_logger = self.get_or_create_s3_audit_logger()
        s3_audit_logger.log(log_data)

    def write_log_to_s3(self, full_object_key, log_data):
        """
        Writes the log data to the S3 bucket.

        Args:
            full_object_key (str): The full S3 object key where the log data will be stored.
            log_data (ShieldAudit): The audit data to log.

        Raises:
            ShieldException: If there is an error uploading logs to S3.
        """
        try:
            response = self.s3_client.put_object(
                Body=json.dumps(log_data.__dict__),
                Bucket=self.bucket_name,
                Key=full_object_key
            )

            logger.debug(f"Logs uploaded successfully:{response}")
        except Exception as e:
            logger.error(f"Error uploading logs to S3=> {type(e).__name__}: {str(e)} \n{traceback.format_exc()}")
            raise ShieldException(f"Error uploading logs to S3=> {type(e).__name__}: {str(e)}")

    def get_or_create_s3_audit_logger(self):
        if self.s3_audit_logger is None:
            self.s3_audit_logger = S3AuditLogger(self, self.audit_spool_dir,
                                                 self.max_queue_size,
                                                 self.audit_event_queue_timeout_sec)
            self.s3_audit_logger.daemon = True
            self.s3_audit_logger.start()
        return self.s3_audit_logger
