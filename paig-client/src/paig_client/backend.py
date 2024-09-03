import json
import logging
import threading
import time

import urllib3
from urllib3 import Timeout, Retry

from . import util
from .PluginAccessRequestEncryptor import PluginAccessRequestEncryptor
from .exception import PAIGException
from .message import ErrorMessage
from .model import ConversationType, ResponseMessage
from .util import AtomicCounter

_logger = logging.getLogger(__name__)

sequence_number = AtomicCounter()


class ShieldAccessRequest:
    def __init__(self, **kwargs):
        """
        Initialize a ShieldAccessRequest instance.

        Args:
            application_key (str): The Key of the application.
            client_application_key (str): The Key of the client application.
            conversation_thread_id (str): The ID of the conversation thread.
            stream_id (str): The ID of the conversation stream.
            request_id (str): The Request ID.
            user_name (str): The name of the user making the request.
            context (dict): The dictionary containing extra information about request.
            request_text (list[str]): The text of the request.
            conversation_type (str): The type of conversation (prompt or reply).

        Note:
            - The conversation_type should be one of the values defined in the ConversationType enum.

        """
        self.application_key = kwargs.get('application_key')
        self.client_application_key = kwargs.get('client_application_key')
        self.conversation_thread_id = kwargs.get('conversation_thread_id')
        self.stream_id = kwargs.get('stream_id', None)
        self.request_id = kwargs.get('request_id')
        self.user_name = kwargs.get('user_name')
        self.context = kwargs.get('context', {})
        self.request_text = kwargs.get('request_text')
        self.conversation_type = kwargs.get('conversation_type', ConversationType.PROMPT)
        self.shield_server_key_id = kwargs.get('shield_server_key_id', None)
        self.shield_plugin_key_id = kwargs.get('shield_plugin_key_id', None)
        self.enable_audit = kwargs.get('enable_audit', True)

    def to_payload_dict(self):
        """
        Serialize the ShieldAccessRequest instance to a JSON string.

        Returns:
            str: JSON representation of the instance.
        """
        request_dict = {
            # "conversationId": "1001", # Not able to get

            "threadId": self.conversation_thread_id,
            "streamId": self.stream_id,
            "requestId": self.request_id,

            "sequenceNumber": sequence_number.increment(),
            "requestType": self.conversation_type.lower(),

            "requestDateTime": int(time.time()) * 1000,
            # datetime.now(timezone.utc),
            # utils.get_time_now_utc_str(), # TODO: this is a breaking change from int to iso8601 time format

            "clientApplicationKey": self.client_application_key,
            "applicationKey": self.application_key,

            "userId": self.user_name,

            "context": self.context,  # Additional context information
            "messages": self.request_text,

            "clientIp": util.get_my_ip_address(),
            "clientHostName": util.get_my_hostname(),

            "shieldServerKeyId": self.shield_server_key_id,
            "shieldPluginKeyId": self.shield_plugin_key_id,

            "enableAudit": self.enable_audit
        }

        return request_dict

    @classmethod
    def create_request_context(cls, paig_plugin):
        context = {}

        vector_db_info = paig_plugin.get_current("vectorDBInfo", default_value=None)
        if vector_db_info is not None:
            context["vectorDBInfo"] = vector_db_info
            paig_plugin.set_current(vectorDBInfo=None)

        # This is needed to update the tokens position in analyzerResult
        stream_sentence_length = paig_plugin.get_current("stream_sentence_length", default_value=None)
        if stream_sentence_length is not None:
            context["previous_sentence_length"] = stream_sentence_length
            paig_plugin.set_current(stream_sentence_length=None)

        return context


class ShieldAccessResult:
    def __init__(self, **kwargs):
        """
        Initialize a ShieldAccessResult instance.

        Args:
            threadId (str): The ID of the thread.
            requestId (str): The ID of the request.
            sequenceNumber (int): The sequence number.
            isAllowed (bool): Indicates whether the access is allowed.
            responseMessages (list): A list of response messages.

        Attributes:
            threadId (str): The ID of the thread.
            requestId (str): The ID of the request.
            sequenceNumber (int): The sequence number.
            isAllowed (bool): Indicates whether the access is allowed.
            responseMessages (list): A list of response messages.
        """
        self.threadId = kwargs.get('threadId')
        self.requestId = kwargs.get('requestId')
        self.sequenceNumber = kwargs.get('sequenceNumber')
        self.isAllowed = kwargs.get('isAllowed')
        self.responseMessages = kwargs.get('responseMessages')

    @classmethod
    def from_json(cls, **response_dict):
        """
        Deserialize a JSON string to create a ShieldAccessResult instance.

        Args:
            response_dict (str): JSON representation of the ShieldAccessResult.

        Returns:
            ShieldAccessResult: An instance of ShieldAccessResult.
        """
        return cls(**response_dict)

    def get_response_messages(self):
        """
        Get a list of ResponseMessage instances from 'responseMessages'.

        Returns:
            list: A list of ResponseMessage instances.
        """
        response_messages = []
        for message in self.responseMessages:
            response_messages.append(ResponseMessage(message['responseText']))
        return response_messages

    def get_last_response_message(self) -> ResponseMessage:
        """
        Get the last ResponseMessage in the 'responseMessages' list.

        Returns:
            ResponseMessage: The last ResponseMessage.

        Raises:
            Exception: If no responseMessages are found.
        """
        if len(self.responseMessages) == 0:
            raise Exception("No responseMessages found.")

        last_response_message = self.responseMessages[-1]
        return ResponseMessage(last_response_message['responseText'])

    def get_is_allowed(self):
        """
        Get the 'isAllowed' attribute value.

        Returns:
            bool: True if access is allowed, False otherwise.
        """
        return self.isAllowed


class VectorDBAccessRequest:
    """
            Initialize a VectorDBAccessRequest instance.

            Args:
                application_key (str): The Key of the application.
                client_application_key (str): The Key of the client application.
                conversation_thread_id (str): The ID of the conversation thread.
                request_id (str): The Request ID.
                user_name (str): The name of the user making the request.
                request_text (list[str]): The text of the request.
                conversation_type (str): The type of conversation (prompt or reply).
            """

    def __init__(self, **kwargs):
        self.application_key = kwargs.get('application_key')
        self.client_application_key = kwargs.get('client_application_key')
        self.conversation_thread_id = kwargs.get('conversation_thread_id')
        self.request_id = kwargs.get('request_id')
        self.user_name = kwargs.get('user_name')

    def to_payload_dict(self):
        """
                Serialize the VectorDBAccessRequest instance to a JSON string.

                Returns:
                    str: JSON representation of the instance.
        """
        request_dict = {
            "threadId": self.conversation_thread_id,
            "requestId": self.request_id,
            "sequenceNumber": sequence_number.increment(),
            "requestDateTime": int(time.time()) * 1000,
            "clientApplicationKey": self.client_application_key,
            "applicationKey": self.application_key,
            "userId": self.user_name,
            "context": {},  # Additional context information
            "clientIp": util.get_my_ip_address(),
            "clientHostName": util.get_my_hostname(),
        }

        return request_dict


class VectorDBAccessResult:
    """
            Initialize a VectorDBAccessResult instance.

            Args:
                filterExpression (str): Row level filter expression policy

            Attributes:
                filterExpression (str): Row level filter expression policy
    """

    def __init__(self, **kwargs):
        self.vectorDBPolicyInfo = kwargs.get('vectorDBPolicyInfo')
        self.vectorDBId = kwargs.get('vectorDBId')
        self.vectorDBName = kwargs.get('vectorDBName')
        self.vectorDBType = kwargs.get('vectorDBType')
        self.userEnforcement = kwargs.get('userEnforcement')
        self.groupEnforcement = kwargs.get('groupEnforcement')
        self.filterExpression = kwargs.get('filterExpression')

    @classmethod
    def from_json(cls, **response_dict):
        """
                Deserialize a JSON string to create a ShieldAccessResult instance.

                Args:
                    response_dict (str): JSON representation of the ShieldAccessResult.

                Returns:
                    VectorDBAccessResult: An instance of VectorDBAccessResult.
                """
        return cls(**response_dict)

    def get_filter_expression(self):
        """
        Get the 'filter_expression' attribute value.

        Returns:
            str: returns filter expression .
        """
        return self.filterExpression


class StreamAccessAuditRequest:

    def __init__(self, **kwargs):
        """
        Initializes a StreamAccessAuditRequest object.

        Keyword Arguments:
            event_time (str): The timestamp of the event.
            tenant_id (str): The ID of the tenant.
            conversation_id (str): The ID of the conversation.
            request_id (str): The ID of the request.
            thread_id (str): The ID of the thread.
            thread_sequence_number (int): The sequence number of the thread.
            request_type (ConversationType): The type of request (default is ConversationType.REPLY).
            user_id (str): The ID of the user.
            client_application_key (str): The key of the client application.
            application_key (str): The key of the application.
            application_name (str): The name of the application.
            result (str): The result of the request.
            traits (list): List of traits associated with the request (default is an empty list).
            masked_traits (dict): Dictionary of masked traits (default is an empty dictionary).
            context (dict): Dictionary containing context information (default is an empty dictionary).
            messages (list): List of messages associated with the request (default is an empty list).
            ranger_audit_ids (list): List of Ranger audit IDs (default is an empty list).
            ranger_policy_ids (list): List of Ranger policy IDs (default is an empty list).
            paig_policy_ids (list): List of PAIG policy IDs (default is an empty list).
            client_ip (str): The IP address of the client.
            client_hostname (str): The hostname of the client.
            number_of_tokens (int): The number of tokens (default is 0).
            encryption_key_id (str): The ID of the encryption key (default is None).
        """

        self.event_time = kwargs.get("event_time")
        self.tenant_id = kwargs.get("tenant_id")
        self.conversation_id = kwargs.get("conversation_id")
        self.request_id = kwargs.get("request_id")
        self.thread_id = kwargs.get("thread_id")
        self.thread_sequence_number = kwargs.get("thread_sequence_number")
        self.request_type = kwargs.get("request_type", ConversationType.REPLY)
        self.user_id = kwargs.get("user_id")
        self.client_application_key = kwargs.get("client_application_key")
        self.application_key = kwargs.get("application_key")
        self.application_name = kwargs.get("application_name")
        self.result = kwargs.get("result")
        self.traits = kwargs.get("traits", [])
        self.masked_traits = kwargs.get("masked_traits", {})
        self.context = kwargs.get("context", {})
        self.messages = kwargs.get("messages", [])
        self.ranger_audit_ids = kwargs.get("ranger_audit_ids", [])
        self.ranger_policy_ids = kwargs.get("ranger_policy_ids", [])
        self.paig_policy_ids = kwargs.get("paig_policy_ids", [])
        self.client_ip = kwargs.get("client_ip")
        self.client_hostname = kwargs.get("client_hostname")
        self.number_of_tokens = kwargs.get("number_of_tokens", 0)

        # This is shield server key id
        self.encryption_key_id = kwargs.get('encryption_key_id', None)

    def to_payload_dict(self):
        """
        Returns a dictionary representation of the StreamAccessAuditRequest object.

        Returns:
            dict: A dictionary containing the attributes of the request.
        """

        request_dict = {
            "eventTime": self.event_time,
            "tenantId": self.tenant_id,
            "conversationId": self.conversation_id,
            "requestId": self.request_id,
            "threadId": self.thread_id,
            "threadSequenceNumber": self.thread_sequence_number,
            "requestType": self.request_type,
            "userId": self.user_id,
            "clientApplicationKey": self.client_application_key,
            "applicationKey": self.application_key,
            "applicationName": self.application_name,
            "result": self.result,
            "traits": self.traits,
            "maskedTraits": self.masked_traits,
            "context": self.context,
            "messages": self.messages,
            "rangerAuditIds": self.ranger_audit_ids,
            "rangerPolicyIds": self.ranger_policy_ids,
            "paigPolicyIds": self.paig_policy_ids,
            "clientIp": self.client_ip,
            "clientHostname": self.client_hostname,
            "numberOfTokens": self.number_of_tokens,

            "encryptionKeyId": self.encryption_key_id
        }

        return request_dict

    @classmethod
    def from_payload_dict(cls, payload_dict):
        """
        Creates a StreamAccessAuditRequest object from a dictionary payload.

        Args:
            payload_dict (dict): Dictionary containing attributes of the request.

        Returns:
            StreamAccessAuditRequest: An instance of StreamAccessAuditRequest.
        """
        kwargs = {
            "event_time": payload_dict.get("eventTime"),
            "tenant_id": payload_dict.get("tenantId"),
            "conversation_id": payload_dict.get("conversationId"),
            "request_id": payload_dict.get("requestId"),
            "thread_id": payload_dict.get("threadId"),
            "thread_sequence_number": payload_dict.get("threadSequenceNumber"),
            "request_type": payload_dict.get("requestType"),
            "user_id": payload_dict.get("userId"),
            "client_application_key": payload_dict.get("clientApplicationKey"),
            "application_key": payload_dict.get("applicationKey"),
            "application_name": payload_dict.get("applicationName"),
            "result": payload_dict.get("result"),
            "traits": payload_dict.get("traits", []),
            "masked_traits": payload_dict.get("maskedTraits", {}),
            "context": payload_dict.get("context", {}),
            "messages": payload_dict.get("messages", []),
            "ranger_audit_ids": payload_dict.get("rangerAuditIds", []),
            "ranger_policy_ids": payload_dict.get("rangerPolicyIds", []),
            "paig_policy_ids": payload_dict.get("paigPolicyIds", []),
            "client_ip": payload_dict.get("clientIp"),
            "client_hostname": payload_dict.get("clientHostname"),
            "number_of_tokens": payload_dict.get("numberOfTokens", 0),
            "encryption_key_id": payload_dict.get("encryptionKeyId")
        }
        return cls(**kwargs)


class HttpTransport:
    """
    HttpTransport class maintains a single instance of urllib3.PoolManager for all the ShieldRestHttpClient instances.
    """
    _http: urllib3.PoolManager = None
    _rw_lock = threading.RLock()

    _max_retries = 4
    _backoff_factor = 1
    _allowed_methods = ["GET", "POST", "PUT", "DELETE"]
    _status_forcelist = [500, 502, 503, 504]
    _connect_timeout_sec = 2.0
    _read_timeout_sec = 7.0
    """
    These are default settings that can be overridden by calling the setup method.
    """

    @staticmethod
    def setup(**kwargs):
        """
        This optional method allows you to pass your own instance of the PoolManager to be used by all the
        ShieldRestHttpClient instances.
        :param kwargs:
            - http: Instance of urllib3.PoolManager
            - max_retries
            - backoff_factor
            - allowed_methods
            - status_forcelist
            - connect_timeout_sec
            - read_timeout_sec
        :return:
        """
        HttpTransport._http = kwargs.get('http', HttpTransport._http)
        HttpTransport._max_retries = kwargs.get('max_retries', HttpTransport._max_retries)
        HttpTransport._backoff_factor = kwargs.get('backoff_factor', HttpTransport._backoff_factor)
        HttpTransport._allowed_methods = kwargs.get('allowed_methods', HttpTransport._allowed_methods)
        HttpTransport._status_forcelist = kwargs.get('status_forcelist', HttpTransport._status_forcelist)
        HttpTransport._connect_timeout_sec = kwargs.get('connect_timeout_sec', HttpTransport._connect_timeout_sec)
        HttpTransport._read_timeout_sec = kwargs.get('read_timeout_sec', HttpTransport._read_timeout_sec)

    @staticmethod
    def get_http():
        if not HttpTransport._http:
            HttpTransport.create_default_http()
        return HttpTransport._http

    @staticmethod
    def create_default_http():
        with HttpTransport._rw_lock:
            if not HttpTransport._http:
                # TODO: add proxy support
                # TODO: add ignore SSL support
                # TODO: expose any metrics

                retries = Retry(total=HttpTransport._max_retries,
                                backoff_factor=HttpTransport._backoff_factor,
                                allowed_methods=HttpTransport._allowed_methods,
                                status_forcelist=HttpTransport._status_forcelist)
                timeout = Timeout(connect=HttpTransport._connect_timeout_sec, read=HttpTransport._read_timeout_sec)
                HttpTransport._http = urllib3.PoolManager(maxsize=50, block=True, retries=retries, timeout=timeout)


class ShieldRestHttpClient:
    """
    ShieldRestHttpClient class is the main class that is used to make requests to the Privacera Shield server.
    """

    def __init__(self, **kwargs):
        self.tenant_id = kwargs['tenant_id'] if 'tenant_id' in kwargs else None
        self.base_url = kwargs['base_url']
        self.api_key = kwargs['api_key']
        self.is_self_hosted_shield_server = kwargs.get('is_self_hosted_shield_server', False)

        # you can pass in a dict() in request_kwargs that will added to kwargs of the request method call
        # this will allow you to set custom Timeout or Retry objects for an application
        self.request_kwargs = kwargs.get('request_kwargs', {})
        if 'timeout' not in self.request_kwargs:
            self.request_kwargs['timeout'] = Timeout(connect=2.0, read=7.0)

        self.plugin_access_request_encryptor = PluginAccessRequestEncryptor(self.tenant_id,
                                                                            kwargs["encryption_keys_info"])

    def get_plugin_access_request_encryptor(self):
        return self.plugin_access_request_encryptor

    def get_default_headers(self):
        headers = dict()
        if self.tenant_id:
            headers["x-tenant-id"] = self.tenant_id
        if self.api_key:
            headers["x-paig-api-key"] = self.api_key
        return headers

    def is_access_allowed(self, request: ShieldAccessRequest) -> ShieldAccessResult:
        """
        Check if access is allowed and return the result.

        Args:
            request (ShieldAccessRequest): The access request to be checked.

        Returns:
            ShieldAccessResult: The result of the access check.
        """

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Access request parameters: {request.to_payload_dict()}")

        # Encrypt the request messages and set the encryption key id and plugin public key in request
        self.plugin_access_request_encryptor.encrypt_request(request)

        request.shield_server_key_id = self.plugin_access_request_encryptor.shield_server_key_id
        request.shield_plugin_key_id = self.plugin_access_request_encryptor.shield_plugin_key_id

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Access request parameters (encrypted): {request.to_payload_dict()}")

        response = HttpTransport.get_http().request(method="POST",
                                                    url=self.base_url + "/shield/authorize",
                                                    headers=self.get_default_headers(),
                                                    json=request.to_payload_dict(),
                                                    **self.request_kwargs)

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Access response status (encrypted): {response.status}, body: {response.data}")

        if response.status == 200:
            access_result = ShieldAccessResult.from_json(**response.json())
            if access_result.isAllowed:
                # Decrypt the response messages
                self.plugin_access_request_encryptor.decrypt_response(access_result)
                if _logger.isEnabledFor(logging.DEBUG):
                    _logger.debug(
                        f"Access response status: {response.status}, access_result: {json.dumps(access_result.__dict__)}")
            return access_result
        else:
            error_message = f"Request failed with status code {response.status}: {response.data}"
            _logger.error(error_message)
            raise Exception(error_message)

    def init_shield_server(self, application_key) -> None:
        """
        Initialize shield server for the tenant id.
        """

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Initializing shield server for tenant: tenant_id={self.tenant_id}")

        request = {"shieldServerKeyId": self.plugin_access_request_encryptor.shield_server_key_id,
                   "shieldPluginKeyId": self.plugin_access_request_encryptor.shield_plugin_key_id,
                   "applicationKey": application_key}

        error_message = ""
        init_success = False
        response_status = 0

        try:
            response = HttpTransport.get_http().request(method="POST",
                                                        url=self.base_url + "/shield/init",
                                                        headers=self.get_default_headers(),
                                                        json=json.dumps(request),
                                                        **self.request_kwargs)

            response_status = response.status

            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug(f"Shield server initialization response status: {response.status}, body: {response.data}")

            if response_status == 200:
                init_success = True
                _logger.info(f"Shield server initialized for tenant: tenant_id={self.tenant_id}")
            else:
                if response_status == 400 or response_status == 404:
                    error_message = str(response.data)
                    error_message += (
                        "\n\nThe request sent to the shield server for initialization is invalid or malformed.\n\n"
                        "To resolve this issue, please verify the configuration file for the plugin.\n"
                        "Try re-downloading the configuration file from the PAIG Portal and restarting your application to ensure that the configuration is correct.\n\n"
                        "For detailed instructions, please follow the guidance provided in the integration documentation at https://na.privacera.ai/docs/integration/.\n"
                        "If the issue persists after performing the above steps, please contact Privacera Support for further assistance."
                    )
                elif response_status == 500:
                    error_message = str(response.data)
                    error_message += (
                        "\n\nThe server encountered an unexpected condition that prevented it from fulfilling the request.\n\n"
                        "Please contact Privacera Support for further assistance."
                    )
        except Exception as e:
            error_message = (
                "\n\nThe Privacera Shield Plugin is unable to establish a connection with the Privacera Shield Server.\n"
                "Please ensure that the Shield Server is up and running and is reachable from the current environment where this application is being executed."
            )

            if not self.is_self_hosted_shield_server:
                error_message += (
                    "\n\nFor privacera.ai hosted shield server, verify https://status.privacera.com for any reported downtime.\n"
                    "If the issue persists after performing the above steps, please contact Privacera Support for further assistance."
                )

        if not init_success:
            message = ErrorMessage.SHIELD_SERVER_INITIALIZATION_FAILED.format(response_status=response_status,
                                                                              response_data=error_message)
            _logger.error(message)
            raise PAIGException(message)

    def get_filter_expression(self, request: VectorDBAccessRequest) -> VectorDBAccessResult:

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Vector DB Access request parameters: {request.to_payload_dict()}")

        response = HttpTransport.get_http().request(method="POST",
                                     url=self.base_url + "/shield/authorize/vectordb",
                                     headers=self.get_default_headers(),
                                     json=request.to_payload_dict(),
                                     **self.request_kwargs)

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Response status: {response.status}, body: {response.data}")

        if response.status == 200:
            return VectorDBAccessResult.from_json(**response.json())
        else:
            error_message = f"Request failed with status code {response.status}: {response.data}"
            _logger.error(error_message)
            raise Exception(error_message)

    def log_stream_access_audit(self, request: StreamAccessAuditRequest):
        """
        Logs a stream access audit request.

        Args:
            request (StreamAccessAuditRequest): The StreamAccessAuditRequest object containing the audit details.

        Returns:
            None
        """

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Stream access audit request parameters: {request.to_payload_dict()}")

        response = HttpTransport.get_http().request(method="POST",
                                                    url=self.base_url + "/shield/audit",
                                                    headers=self.get_default_headers(),
                                                    json=request.to_payload_dict(),
                                                    **self.request_kwargs)

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Stream access audit response status : {response.status}, body: {response.data}")

        if response.status == 200:
            if _logger.isEnabledFor(logging.DEBUG):
                _logger.debug(
                    f"Stream access audit response status: {response.status}, access_result: {json.dumps(response.__dict__)}")
        else:
            error_message = f"Stream access audit request failed with status code {response.status}: {response.data}"
            _logger.error(error_message)
            raise Exception(error_message)