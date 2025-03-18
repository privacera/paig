import json
import logging
import os
import threading
import time
import uuid
import base64
from queue import Queue
import contextvars

from . import interceptor_setup, util
from paig_common.audit_spooler import AuditLogger
from .backend import ShieldRestHttpClient, ShieldAccessRequest, HttpTransport, VectorDBAccessRequest, \
    ShieldAccessResult, StreamAccessAuditRequest
from .exception import PAIGException, AccessControlException
from .message import ErrorMessage, InfoMessage, WarningMessage
from .model import ConversationType
from .posthog_events.posthog import capture_setup_event

_logger = logging.getLogger(__name__)


class PAIGPlugin:
    """
    Base plugin for Privacera AI Governance (PAIG).

    This class provides the foundational functionality for PAIG plugins,
    including method interception and user_name context management.

    Attributes:
        enable_privacera_shield (bool): Whether to enable Privacera Shield.
        frameworks (list): The list of frameworks to intercept methods from.
        user_context: An instance of contextvars.ContextVar() for managing thread-chain data.
        thread_local_rlock: An instance of threading.RLock() for thread-local data locking.
        interceptor_installer_list: A list of interceptor installers for the PAIG plugin.
    """

    USER_CONTEXT = "user_context"
    """This is the key stored in thread-local storage for the user_name context."""

    def __init__(self, **kwargs):
        """
        Initializes an instance of the PAIGPlugin class.

        Args:
            kwargs: The name-value pairs to be set in the context. The following are the supported options:

                enable_privacera_shield (bool): Whether to enable Privacera Shield.

                frameworks (list): The list of frameworks to intercept methods from.

                http: An instance of urlib3.PoolManager to be used by the PAIG plugin.

                max_retries (int): The maximum number of retries for HTTP requests.

                backoff_factor (int): The backoff factor for HTTP retries.

                allowed_methods (list): The list of HTTP methods allowed for retry.

                status_retry_forcelist (list): The list of HTTP status codes for which retry is forced.

                connection_timeout (float): The connection timeout for the access request.

                read_timeout (float): The read timeout for the access request.
        """

        try:
            # TODO need to pass a flag saying this is default app
            # for default app we can look in the folder and pick any config file
            # but when creating a new app we need to pass the config file
            self.default_application = PAIGApplication(**kwargs)
            if not self.default_application.is_configured():
                self.default_application = None
        except PAIGException as e:
            if str(ErrorMessage.SHIELD_SERVER_INITIALIZATION_FAILED.value[0]) in e.args[0]:
                raise e
            else:
                self.default_application = None
        except:
            self.default_application = None

        # Init from the loaded file
        self.enable_privacera_shield = kwargs.get("enable_privacera_shield",
                                                  os.getenv("PRIVACERA_SHIELD_ENABLE", "true").lower() == "true")
        _logger.info(
            InfoMessage.PRIVACERA_SHIELD_IS_ENABLED.format(is_enabled=self.enable_privacera_shield))

        self.interceptor_installer_list = None

        self.frameworks = None
        if "frameworks" in kwargs:
            self.frameworks = kwargs["frameworks"]
            capture_setup_event(frameworks=self.frameworks)
        else:
            raise PAIGException(ErrorMessage.FRAMEWORKS_NOT_PROVIDED)

        HttpTransport.setup(**kwargs)

        self.user_context = contextvars.ContextVar(PAIGPlugin.USER_CONTEXT)
        self.thread_local_rlock = threading.RLock()

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"PAIGPlugin initialized with {self.__dict__}")

    def get_frameworks_to_intercept(self):
        return self.frameworks

    def get_current_application(self):
        application = self.get_current("application")
        if not application:
            if not self.default_application:
                raise PAIGException(ErrorMessage.APPLICATION_NOT_PROVIDED)
            else:
                return self.default_application
        else:
            return application

    def get_shield_client(self):
        return self.get_current_application().get_shield_client()

    def get_application_key(self):
        return self.get_current_application().get_application_key()

    def get_client_application_key(self):
        return self.get_current_application().get_client_application_key()

    def setup(self):
        """
        Set up the PAIG plugin by intercepting methods for enhanced functionality.
        """
        if self.enable_privacera_shield:
            self.interceptor_installer_list = interceptor_setup.setup(self)

    def undo_setup(self):
        """
        Undo the setup of the PAIG plugin by removing the method interceptors. Usually used for testing.
        :return:
        """
        for interceptor_installer in self.interceptor_installer_list:
            interceptor_installer.undo_setup_interceptors()

    def set_current_user(self, username):
        """
        Set the current user_name context for the PAIG plugin.

        Args:
            username (str): The username of the current user_name.

        Notes:
            This method needs to be called before making any request to LLM
        """
        self.set_current(username=username)

    def get_current_user(self):
        """
        Get the current user_name from the PAIG plugin's context.

        Returns:
            str: The username of the current user_name.

        Raises:
            Exception: If the current user_name is not set in the context.
        """
        return self.get_current("username")

    def get_llm_stream_access_checker(self):
        """
        Retrieve an instance of the LLMStreamAccessChecker for this object.

        This method retrieves an existing instance of the LLMStreamAccessChecker
        associated with this object if one exists.

        Returns:
            LLMStreamAccessChecker: An instance of the LLMStreamAccessChecker,
            or raises RuntimeError if one does not exist.

        Raises:
            RuntimeError: If no instance of LLMStreamAccessChecker exists.
        """
        llm_stream_access_checker = self.get_current("llm_stream_access_checker")
        if llm_stream_access_checker is None:
            raise RuntimeError("LLMStreamAccessChecker instance does not exist.")
        return llm_stream_access_checker

    def create_llm_stream_access_checker(self):
        """
        Create a new instance of the LLMStreamAccessChecker for this object.

        This method creates a new instance of the LLMStreamAccessChecker
        associated with this object if one does not already exist.

        Returns:
            LLMStreamAccessChecker: A new instance of the LLMStreamAccessChecker.
        """
        llm_stream_access_checker = LLMStreamAccessChecker(self)
        self.set_current(llm_stream_access_checker=llm_stream_access_checker)

    def get_or_create_llm_stream_audit_logger(self):
        """
        Gets or creates an instance of StreamAuditLogger.

        Returns:
            StreamAuditLogger: An instance of StreamAuditLogger.
        """
        return self.get_current_application().get_or_create_llm_stream_audit_logger()

    def log_stream_access_audit(self, audit_log_request: StreamAccessAuditRequest):
        """
        Logs a stream access audit.

        Args:
            audit_log_request (StreamAccessAuditRequest): The StreamAccessAuditRequest object containing the audit log details.
        """
        self.get_current_application().log_stream_access_audit(audit_log_request)

    def cleanup_llm_stream_access_checker(self):
        """
        Clean up the existing instance of LLMStreamAccessChecker, if any.

        This method cleans up any existing instance of the LLMStreamAccessChecker
        associated with this object.
        """
        existing_instance = self.get_current("llm_stream_access_checker")
        if existing_instance is not None:
            # Clean up any resources or perform necessary cleanup operations
            # Note: This depends on the implementation of LLMStreamAccessChecker
            del existing_instance  # Delete the existing instance

        self.set_current(llm_stream_access_checker=None)

    def generate_request_id(self):
        """
        Generate a unique Request ID.

        Returns:
            str: A unique Request ID in UUID format.
        """
        return str(uuid.uuid4())

    def generate_conversation_thread_id(self):
        """
        Generate a unique Thread ID for the conversation.

        Returns:
            str: A unique Thread ID in UUID format.
        """
        return str(uuid.uuid4())

    def get_user_context(self):
        """
        Retrieve the current user context.

        This method retrieves the current user context from the context variable. If no user context
        is set, it returns an empty dictionary.

        Returns:
            dict: The current user context if set, otherwise an empty dictionary.
        """
        user_context = self.user_context.get(None)
        if user_context is None:
            user_context = {}
        return user_context

    def set_user_context(self, user_context):
        """
        Set the user context.

        This method sets the user context in the context variable. The user context should be a
        dictionary containing user-specific data.

        Parameters:
            user_context (dict): The user context to set.
        """
        self.user_context.set(user_context)

    def set_current(self, **kwargs):
        """
        Set any name-value into current thread-local context for the PAIG plugin.
        :param kwargs: name=value pairs to be set in the context
        :return: nothing
        """
        with self.thread_local_rlock:
            user_context = self.get_user_context()
            user_context.update(kwargs)
            self.set_user_context(user_context)

    def get_current(self, key, default_value=None):
        """
        Get the value of the given key from the current thread-local context for the PAIG plugin.
        :param key:
        :param default_value: returned if the key does not exist
        :return:
        """
        with self.thread_local_rlock:
            user_context = self.get_user_context()
            if key in user_context:
                return user_context[key]
            else:
                return default_value

    def clear(self):
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug("Clearing thread-local context for PAIG plugin")
        with self.thread_local_rlock:
            self.set_user_context(None)

    def check_access(self, **kwargs):
        return self.get_current_application().check_access(**kwargs)

    def get_vector_db_filter_expression(self, **kwargs):
        return self.get_current_application().get_vector_db_filter_expression(**kwargs)


class PAIGPluginContext:
    """
    This class provides a context manager for the PAIG plugin.
    """

    def __init__(self, **kwargs):
        """
        Initializes an instance of the PAIGPluginContext class.

        Args:
            kwargs: The name-value pairs to be set in the context.

        Attributes:
            kwargs: The name-value pairs to be set in the context.
        """
        self.kwargs = kwargs

    def __enter__(self):
        """
        Set the name-value pairs in the context.

        Returns:
            PAIGPluginContext: The current instance of the PAIGPluginContext class.
        """
        global _paig_plugin
        _paig_plugin.set_current(**self.kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Clear the context.

        Args:
            exc_type: The type of the exception.
            exc_val: The exception value.
            exc_tb: The exception traceback.
        """
        global _paig_plugin
        _paig_plugin.clear()


# Global variable to store the PAIGPlugin instance
_paig_plugin: PAIGPlugin = None


def setup(**options):
    """
    This function initializes the PAIGPlugin instance and calls its 'init' method to set up the PAIG plugin.

    Note:
        The global '_paig_plugin' variable is used to store the PAIGPlugin instance for later use.

    """
    global _paig_plugin
    if _paig_plugin is not None:
        _logger.error(ErrorMessage.PAIG_IS_ALREADY_INITIALIZED.format())
    else:
        _paig_plugin = PAIGPlugin(**options)  # Create an instance of PAIGPlugin
        _paig_plugin.setup()  # Initialize the PAIG plugin
        if _logger.isEnabledFor(logging.INFO):
            _logger.info(InfoMessage.PAIG_IS_INITIALIZED.format(kwargs=options))


def set_current_user(username):
    """
    Set the current user_name context for the PAIG plugin.

    Args:
        username (str): The username of the current user_name.

    Note:
        This function sets the user_name context using the 'set_current_user_context' method of the PAIGPlugin instance
        stored in the global '_paig_plugin' variable.

    """
    global _paig_plugin
    _paig_plugin.set_current_user(username)  # Set the current user_name


def get_current_user():
    global _paig_plugin
    return _paig_plugin.get_current("username")


def set_current(**kwargs):
    global _paig_plugin
    _paig_plugin.set_current(**kwargs)


def get_current(key, default_value=None):
    global _paig_plugin
    ret_val = _paig_plugin.get_current(key, default_value)
    return ret_val


def clear():
    global _paig_plugin
    _paig_plugin.clear()


def create_shield_context(**kwargs):
    return PAIGPluginContext(**kwargs)


def check_access(**kwargs):
    global _paig_plugin
    return _paig_plugin.check_access(**kwargs)


def get_vector_db_filter_expression(**kwargs):
    global _paig_plugin
    return _paig_plugin.get_vector_db_filter_expression(**kwargs)


def dummy_access_denied():
    raise AccessControlException("Access Denied")


def setup_app(**kwargs):
    """
    This function creates an instance of PAIGApplication from the application config file.
    Args:
        kwargs: The following are the supported options.
            application_config_file: The path to the application config file.
            application_config: The application config dictionary or string contents of the file
            request_kwargs: The keyword arguments to be passed to the urllib3.request call and can contain
            timeout and retry objects
            application_config_api_key: The API key to fetch the application config from the PAIG Server
    Returns:
        Instance of PAIGApplication
    """
    if "application_config_file" in kwargs or "application_config" in kwargs or "application_config_api_key" in kwargs:
        app = PAIGApplication(**kwargs)
        if app.is_configured():
            return app
        else:
            raise PAIGException(ErrorMessage.APPLICATION_NOT_CONFIGURED)
    else:
        raise PAIGException(ErrorMessage.PARAMETERS_FOR_APP_CONFIG_NOT_PROVIDED)


class PAIGApplication:
    """
     Base plugin for Privacera AI Governance (PAIG).

     This class provides the foundational functionality for PAIG plugins,
     including method interception and user_name context management.

     Attributes:
         client_application_key (str): The client application id for the client making requests.
         application_id (str): The application id for the client making requests.
         application_key (str): The application key for the client making requests.
         tenant_id (str): The ID of the tenant using the plugin.
         shield_base_url (str): The base URL for the Shield service.
         api_key (str): The API key.
         shield_server_key_id (str): The key ID for the Shield server.
         shield_server_public_key (str): The public key for the Shield server.
         shield_plugin_key_id (str): The key ID for the Shield plugin.
         shield_plugin_private_key (str): The private key for the Shield plugin.
         shield_client: An instance of the ShieldRestHttpClient class for making requests to the Shield service.
         request_kwargs: The keyword arguments to be passed to the ShieldRestHttpClient class.
     """

    def __init__(self, **kwargs):
        """
        Initializes an instance of the PAIGPlugin class.

        Args:
            kwargs: The following are the supported options.
                application_config_file (str): The path to the application config file.
                application_config (dict): The application config dictionary or string contents of the file
                request_kwargs (dict): The keyword arguments to be passed to the ShieldRestHttpClient class.
                application_config_api_key (str): The API key to fetch the application config from the PAIG Server

                You can also pass in any of the keys from the application config file as keyword arguments in case
                you want to override the values that are in the application config file.
        """

        plugin_app_config_dict = self.get_plugin_app_config(kwargs)

        # Init from the loaded file
        self.client_application_key = plugin_app_config_dict.get("clientApplicationKey", "*")
        self.application_id = plugin_app_config_dict.get("applicationId")
        self.application_key = plugin_app_config_dict.get("applicationKey")
        self.tenant_id = plugin_app_config_dict.get("tenantId")

        is_self_hosted_shield_server = False
        shield_server_url = plugin_app_config_dict.get("shieldServerUrl")
        if shield_server_url is not None:
            self.shield_base_url = shield_server_url
            is_self_hosted_shield_server = True
        else:
            self.shield_base_url = plugin_app_config_dict.get("apiServerUrl")

        self.api_key = plugin_app_config_dict.get("apiKey")
        self.shield_server_key_id = plugin_app_config_dict.get("shieldServerKeyId")
        self.shield_server_public_key = plugin_app_config_dict.get("shieldServerPublicKey")
        self.shield_plugin_key_id = plugin_app_config_dict.get("shieldPluginKeyId")
        self.shield_plugin_private_key = plugin_app_config_dict.get("shieldPluginPrivateKey")
        self.audit_spool_dir = plugin_app_config_dict.get("auditSpoolDir", "spool/audits/")

        # Allow override from kwargs
        for key, value in kwargs.items():
            if key in self.__dict__:
                self.__dict__[key] = value

        encryption_keys_info = {
            "shield_server_key_id": self.shield_server_key_id,
            "shield_server_public_key": self.shield_server_public_key,
            "shield_plugin_key_id": self.shield_plugin_key_id,
            "shield_plugin_private_key": self.shield_plugin_private_key
        }

        self.shield_client = ShieldRestHttpClient(base_url=self.shield_base_url, tenant_id=self.tenant_id,
                                                  api_key=self.api_key, encryption_keys_info=encryption_keys_info,
                                                  request_kwargs=kwargs.get("request_kwargs", {}),
                                                  is_self_hosted_shield_server=is_self_hosted_shield_server)

        self.shield_client.init_shield_server(self.application_key)

        self.llm_stream_audit_logger = None

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"PAIGPlugin initialized with {self.__dict__}")

    @classmethod
    def get_plugin_app_config(self, kwargs):
        """
        Get the plugin application config from the given kwargs. User could pass the entire application config
        file contents in application_config parameter or pass the path to the application config file in
        application_config_file parameter.
        :param kwargs:
        :return: application_config as a dictionary
        """
        if "application_config" in kwargs:
            if isinstance(kwargs["application_config"], str):
                try:
                    plugin_app_config_dict = json.loads(kwargs["application_config"])
                except Exception as e:
                    raise PAIGException(ErrorMessage.INVALID_APPLICATION_CONFIG_FILE.format(error_message=e))
            elif isinstance(kwargs["application_config"], dict):
                plugin_app_config_dict = kwargs["application_config"]
            else:
                raise PAIGException(ErrorMessage.INVALID_APPLICATION_CONFIG_FILE_DATA.format())
        elif "application_config_api_key" in kwargs:
            api_key = kwargs.get("application_config_api_key")
            plugin_app_config_dict = self.fetch_application_config_from_server(api_key, kwargs)
        else:
            api_key = os.environ.get('PAIG_APP_API_KEY')
            plugin_app_config_dict = self.fetch_application_config_from_server(api_key, kwargs)

        return plugin_app_config_dict

    @classmethod
    def fetch_application_config_from_server(self, api_key, kwargs):
        """
        Fetch the application configuration from the server using the given API key.
        Else fallback to the application config file.
        :param api_key:
        :param kwargs:
        :return:
        """
        if not api_key:
            return self.read_options_from_app_config(kwargs.get("application_config_file"))

        try:
            decoded_bytes = base64.urlsafe_b64decode(api_key)
            decoded_str = decoded_bytes.decode('utf-8')
            parts = decoded_str.split(";")
            if len(parts) != 2:
                raise ValueError(
                    "Decoded API key is not in the expected format: 'apiKey;serverUrl'. "
                    "Please provide a valid API key."
                )

            server_url = parts[1]
            if not server_url.startswith("https://"):
                raise ValueError("Invalid server URL format found in API key. please Ensure API key is valid")

            request_url = f"{server_url.rstrip('/')}/api/ai/application/config"
            headers = {"x-paig-api-key": api_key}
            _logger.debug(f"Constructed request URL for fetching application json: {request_url} with headers : {headers}")

            response = HttpTransport.get_http().request(method="GET",
                                                        url=request_url,
                                                        headers=headers)
            if response.status != 200:
                raise ValueError(f"Failed to fetch configuration: HTTP {response.status} {response.data}")

            _logger.debug("Application configuration fetched successfully.")

            plugin_app_config_dict = response.json()
            plugin_app_config_dict.update({
                "apiServerUrl": server_url,
                "apiKey": api_key
            })
        except Exception as e:
            _logger.error("Failed to retrieve application config. Error occurred while processing API key: %s", e, exc_info=True)
            raise ValueError("Failed to fetch configuration from the server. Please ensure API key is valid.")

        return plugin_app_config_dict

    @classmethod
    def read_options_from_app_config(self, application_config_file=None):
        """
        Read the options from the application config file.
        :param application_config_file: application config file name
        :return: application config as a dictionary
        """
        # first check if the file path is in the parameter
        if application_config_file:
            if not os.path.exists(application_config_file):
                raise PAIGException(
                    WarningMessage.APP_CONFIG_FILE_NOT_FOUND_IN_PARAMETER.format(file_path=application_config_file))
            else:
                _logger.info(InfoMessage.USING_CONFIG_FILE_FROM_PARAMETER.format(file_path=application_config_file))
                return self.load_plugin_application_configs_from_file(application_config_file)

        # Get the application config file path from the environment variable
        application_config_file = os.getenv("PRIVACERA_SHIELD_CONF_FILE")
        if application_config_file:
            if not os.path.exists(application_config_file):
                raise PAIGException(
                    ErrorMessage.APP_CONFIG_FILE_IN_ENV_NOT_FOUND.format(file_path=application_config_file))
            else:
                if not os.path.isfile(application_config_file):
                    raise PAIGException(
                        ErrorMessage.APP_CONFIG_FILE_IN_ENV_NOT_FOUND.format(file_path=application_config_file))
                _logger.info(InfoMessage.USING_CONFIG_FILE_FROM_ENV_VAR.format(file_path=application_config_file))
                return self.load_plugin_application_configs_from_file(application_config_file)
        else:
            # If the environment variable is not set, look in the local directory
            application_config_file = PAIGApplication.find_config_file()
            if application_config_file:
                _logger.info(InfoMessage.USING_CONFIG_FILE_FROM_FOLDER.format(file_path=application_config_file))
                return self.load_plugin_application_configs_from_file(application_config_file)

        raise PAIGException(ErrorMessage.API_KEY_NOT_PROVIDED)

    @staticmethod
    def find_config_file():
        application_config_dir = os.getenv("PRIVACERA_SHIELD_CONF_DIR", os.path.join(os.getcwd(), "privacera"))
        if not os.path.exists(application_config_dir):
            _logger.warning(
                WarningMessage.APP_CONFIG_FILE_NOT_FOUND_NO_DEFAULT_FOLDER.format(file_path=application_config_dir))
            return None

        app_config_files = [filename for filename in os.listdir(application_config_dir) if
                            filename.startswith("privacera-shield-") and filename.endswith("-config.json")]
        if len(app_config_files) == 1:
            return os.path.join(application_config_dir, app_config_files[0])
        else:
            raise PAIGException(
                ErrorMessage.MULTIPLE_APP_CONFIG_FILES_FOUND.format(application_config_dir=application_config_dir))

    @classmethod
    def load_plugin_application_configs_from_file(self, app_config_file_path: str):
        with open(app_config_file_path, 'r') as config_file:
            plugin_app_config_dict = json.load(config_file)
            return plugin_app_config_dict

    def is_configured(self):
        return (self.application_id and
                self.application_key and
                self.api_key and
                self.tenant_id and
                self.shield_base_url and
                self.shield_server_key_id and
                self.shield_server_public_key and
                self.shield_plugin_key_id and
                self.shield_plugin_private_key)

    def get_shield_client(self):
        return self.shield_client

    def get_application_key(self):
        return self.application_key

    def get_client_application_key(self):
        return self.client_application_key

    def authorize(self, **kwargs) -> ShieldAccessResult:
        access_request = kwargs.get("access_request")
        if access_request is None:
            if "text" not in kwargs:
                raise PAIGException(ErrorMessage.PROMPT_NOT_PROVIDED)
            if "conversation_type" not in kwargs:
                raise PAIGException(ErrorMessage.CONVERSATION_TYPE_NOT_PROVIDED)
            text = kwargs["text"]
            conversation_type = kwargs["conversation_type"]

            global _paig_plugin

            access_request = ShieldAccessRequest(
                application_key=self.get_application_key(),
                client_application_key=self.get_client_application_key(),
                conversation_thread_id=kwargs.get("thread_id", _paig_plugin.generate_conversation_thread_id()),
                stream_id=kwargs.get("stream_id", None),
                request_id=_paig_plugin.generate_request_id(),
                user_name=_paig_plugin.get_current_user(),
                context=ShieldAccessRequest.create_request_context(paig_plugin=_paig_plugin),
                request_text=text if isinstance(text, list) else [text],
                conversation_type=conversation_type,
                enable_audit=kwargs.get("enable_audit", True),
            )
        return self.get_shield_client().is_access_allowed(request=access_request)

    def check_access(self, **kwargs):
        access_result = self.authorize(**kwargs)
        if not access_result.get_is_allowed():
            raise AccessControlException(access_result.get_response_messages()[0].get_response_text())
        else:
            return access_result.get_response_messages()

    def get_vector_db_filter_expression(self, **kwargs):
        access_request = kwargs.get("access_request")
        if access_request is None:
            global _paig_plugin

            access_request = VectorDBAccessRequest(
                application_key=self.get_application_key(),
                client_application_key=self.get_client_application_key(),
                conversation_thread_id=kwargs.get("thread_id", _paig_plugin.generate_conversation_thread_id()),
                request_id=_paig_plugin.generate_request_id(),
                user_name=_paig_plugin.get_current_user()
            )

        access_result = self.get_shield_client().get_filter_expression(request=access_request)
        # In case if there is no policy to be evaluated for current user then we will get blank filter
        shield_filter_expr = access_result.get_filter_expression()
        # Setting the received shield_filter_expr inside context, so we can pass it for auditing when sending next
        # request for prompt authorization
        if shield_filter_expr != "":
            _paig_plugin.set_current(vectorDBInfo=access_result.__dict__)

        return shield_filter_expr

    def get_or_create_llm_stream_audit_logger(self):
        """
        Gets or creates an instance of StreamAuditLogger.

        If the llm_stream_audit_logger attribute is None, creates an instance of StreamAuditLogger with shieldRestHttpClient as input and starts the StreamAuditLogger thread.

        Returns:
            StreamAuditLogger: An instance of StreamAuditLogger.

        """
        if self.llm_stream_audit_logger is None:
            # Create an instance of StreamAuditLogger with shieldRestHttpClient as input
            self.llm_stream_audit_logger = StreamAuditLogger(self.shield_client, self.audit_spool_dir)

            # Start the StreamAuditLogger thread
            self.llm_stream_audit_logger.start()

        return self.llm_stream_audit_logger

    def log_stream_access_audit(self, audit_log_request: StreamAccessAuditRequest):
        """
        Logs a stream access audit.

        Args:
            audit_log_request (StreamAccessAuditRequest): The StreamAccessAuditRequest object containing the audit log details.

        """

        plugin_access_request_encryptor = self.shield_client.get_plugin_access_request_encryptor()

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Stream access audit request parameters: {audit_log_request.to_payload_dict()}")

        # Encrypt the messages and set the encryption key id and plugin public key in request
        messages = audit_log_request.messages
        encrypted_messages = []
        for message in messages:
            message["originalMessage"] = plugin_access_request_encryptor.encrypt_message(
                message["originalMessage"])
            message["maskedMessage"] = plugin_access_request_encryptor.encrypt_message(
                message["maskedMessage"])
            encrypted_messages.append(message)

        audit_log_request.messages = encrypted_messages

        audit_log_request.encryption_key_id = plugin_access_request_encryptor.shield_server_key_id

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"Stream access audit request parameters (encrypted): {audit_log_request.to_payload_dict()}")

        llm_stream_audit_logger = self.get_or_create_llm_stream_audit_logger()
        llm_stream_audit_logger.log(audit_log_request)


class LLMStreamAccessChecker:
    """
    Class for checking access on streaming data using the LLM model.

    This class is responsible for processing LLM reply tokens and checking access
    based on the generated text. It interacts with the PAIG plugin to perform access
    checks and retrieve authorized responses.
    """

    def __init__(self, paig_plugin):
        """
        Initialize the LLMStreamAccessChecker.

        Args:
            paig_plugin: The PAIG plugin instance for performing access checks.
        """
        self.paig_plugin = paig_plugin
        self.stream_id = str(uuid.uuid4())  # Unique stream id to combine chunks for auditing

        self.llm_reply_text = ""  # Accumulates LLM reply tokens

        # To keep a track first token received
        self.is_first_reply_token_received = False

        # Storing the length of previously processed sentence, this is needed to create analyzerResult by shield
        self.processed_sentence_length = 0

        # Storing all the responses received from shield server
        self.shield_access_response_list = []

        self.llm_original_full_reply = ""
        self.llm_masked_full_reply = ""

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"LLMStreamAccessChecker initialized")

    def check_access_for_sentence(self, text):
        """
        Check access for a given sentence.

        This method checks access for the provided sentence by interacting with
        the PAIG plugin and retrieving the shield response text.

        Args:
            text (str): The sentence for which access needs to be checked.

        Returns:
            str: The shield response text indicating the authorized response.
        """
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"LLMStreamAccessChecker::check_access checking access for text={self.llm_reply_text}")

        # Setting the current sentence length in the context, so it will send with the request context as previous
        # sentence length This is needed to provide accurate characters positions in analyzer
        self.paig_plugin.set_current(stream_sentence_length=self.processed_sentence_length)

        access_result = self.paig_plugin.get_current_application().authorize(text=text,
                                                                             conversation_type=ConversationType.REPLY,
                                                                             thread_id=self.paig_plugin.get_current(
                                                                                 "thread_id"),
                                                                             stream_id=self.stream_id,
                                                                             enable_audit=False)

        # Setting the current text length, so it can be used in next sentence authorize request
        self.processed_sentence_length = self.processed_sentence_length + len(text)

        # Add access responses to list
        self.shield_access_response_list.append(access_result)

        # Keeping track of full original reply to create final audit record
        self.llm_original_full_reply += text

        shield_response_text = access_result.get_response_messages()[0].get_response_text()
        if not access_result.get_is_allowed():
            self.llm_reply_text = ""
            raise AccessControlException(shield_response_text)
        else:
            # Keeping track of full masked reply to create final audit record
            self.llm_masked_full_reply += shield_response_text

        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"LLMStreamAccessChecker::check_access shield response text={shield_response_text}")

        return shield_response_text

    def check_access_for_incomplete_sentence(self):
        if self.llm_reply_text != "":
            self.check_access_for_sentence(self.llm_reply_text)
        self.llm_reply_text = ""

    def check_access(self, llm_reply_token):
        """
        Check access based on the LLM reply token.

        This method accumulates LLM reply tokens until a complete sentence is formed,
        then checks access for that sentence and retrieves the authorized response.

        Args:
            llm_reply_token (str): The LLM reply token to process.
        """
        if _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(f"LLMStreamAccessChecker::check_access llm_reply_token={llm_reply_token}")

        # Accumulate LLM reply tokens to form complete sentences
        self.llm_reply_text = self.llm_reply_text + llm_reply_token

        # Initialize variable to store authorized LLM reply text
        authorized_llm_reply_text = ""

        if self.llm_reply_text.endswith(".") or llm_reply_token == "":
            # Full sentence formed; check access for complete sentence
            authorized_llm_reply_text = self.check_access_for_sentence(self.llm_reply_text)

            # Reset LLM reply text as sentence is complete
            self.llm_reply_text = ""
        else:
            if ". " in self.llm_reply_text:
                # Incomplete sentence; split and process
                sentences = self.llm_reply_text.split(". ")

                # Take first sentence
                sentence = sentences[0] + ". "

                # Check access for incomplete sentence
                authorized_llm_reply_text = self.check_access_for_sentence(sentence)

                # Remove processed sentence from accumulated text
                self.llm_reply_text = self.llm_reply_text.replace(sentence, "", 1)

        return authorized_llm_reply_text

    def create_stream_access_audit_request(self):
        # Get the last record from the list
        last_record = self.shield_access_response_list[-1]

        # Get the current event time in milliseconds
        event_time = int(time.time()) * 1000

        # Extract necessary information from the last record
        tenant_id = self.paig_plugin.get_current_application().tenant_id
        conversation_id = getattr(last_record, "conversationId", "")
        request_id = last_record.requestId
        thread_id = last_record.threadId
        thread_sequence_number = last_record.sequenceNumber
        request_type = ConversationType.REPLY
        user_id = self.paig_plugin.get_current("username")
        client_application_key = self.paig_plugin.get_client_application_key()
        application_key = self.paig_plugin.get_application_key()
        application_name = last_record.responseMessages[0]["applicationName"]

        # Initialize variables for processing response messages
        result = "allowed"
        traits = []
        masked_traits = {}
        analyzer_result_list = []
        ranger_audit_ids = []
        ranger_policy_ids = []
        paig_policy_ids = []

        # Get client IP address and hostname
        client_ip = util.get_my_ip_address()
        client_hostname = util.get_my_hostname()

        # Initialize counters for allowed and denied responses
        allowed_count = 0
        denied_count = 0

        # Iterate over all responses from the shield server for the stream
        for record in self.shield_access_response_list:
            # Update counters based on whether the response is allowed or denied
            if record.isAllowed:
                allowed_count += 1
            else:
                denied_count += 1

            # Process each response message
            for response_message in record.responseMessages:
                # Extract traits and masked traits from response message
                traits.extend(response_message["traits"])

                if response_message["maskedTraits"] is not None:
                    masked_traits.update(response_message["maskedTraits"])

                if "analyzerResult" in response_message and response_message["analyzerResult"] is not None:
                    analyzer_result_list.extend(response_message["analyzerResult"])

                # Extract ranger and paig policy IDs
                if "rangerAuditIds" in response_message:
                    ranger_audit_ids.extend(response_message["rangerAuditIds"])
                if "rangerPolicyIds" in response_message:
                    ranger_policy_ids.extend(response_message["rangerPolicyIds"])

                paig_policy_ids.extend(response_message["paigPolicyIds"])

        # Determine the result based on the counters and masked traits
        if denied_count > 0:
            result = "denied"
        elif allowed_count > 0:
            result = "masked" if len(masked_traits) > 0 else "allowed"

        messages = [
            {
                "originalMessage": self.llm_original_full_reply,
                "maskedMessage": self.llm_masked_full_reply,
                "analyzerResult": json.dumps(analyzer_result_list)
            }
        ]

        stream_access_audit_request = StreamAccessAuditRequest(
            event_time=event_time,
            tenant_id=tenant_id,
            conversation_id=conversation_id,
            request_id=request_id,
            thread_id=thread_id,
            thread_sequence_number=thread_sequence_number,
            request_type=request_type,
            user_id=user_id,
            client_application_key=client_application_key,
            application_key=application_key,
            application_name=application_name,
            result=result,
            traits=traits,
            masked_traits=masked_traits,
            messages=messages,
            ranger_audit_ids=ranger_audit_ids,
            ranger_policy_ids=ranger_policy_ids,
            paig_policy_ids=paig_policy_ids,
            client_ip=client_ip,
            client_hostname=client_hostname
        )

        return stream_access_audit_request

    def flush_audits(self):
        """
        Flushes the audit logs.

        This method is responsible for flushing any pending audit logs to the appropriate storage or logging system.

        Returns:
            None
        """
        if len(self.shield_access_response_list) > 0:
            stream_access_audit_request = self.create_stream_access_audit_request()
            self.paig_plugin.log_stream_access_audit(stream_access_audit_request)
        else:
            _logger.warning(f"No stream audits founds to be pushed")


class StreamAuditLogger(AuditLogger):
    """
    A class to log audit data and push it to a server.

    Attributes:
        shield_rest_http_client (object): An object representing the REST HTTP client.
        audit_log_request_queue (Queue): A queue to store audit log data.
    """

    def __init__(self, shield_rest_http_client: ShieldRestHttpClient, audit_spool_dir: str):
        """
        Initializes the StreamAuditLogger.

        Args:
            shield_rest_http_client (object): An object representing the REST HTTP client.
            audit_spool_dir (str): Audit spool directory
        """
        super().__init__(audit_spool_dir=audit_spool_dir, audit_event_cls=StreamAccessAuditRequest)

        self.shield_rest_http_client = shield_rest_http_client

    def push_audit_event_to_server(self, audit_event: StreamAccessAuditRequest):
        self.shield_rest_http_client.log_stream_access_audit(audit_event)