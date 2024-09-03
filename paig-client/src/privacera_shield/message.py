import logging
from enum import Enum


def unique_message_enum(cls):
    """
    Decorator to check if the enum values are unique
    :param cls: Enum class
    :return: Enum class
    """
    used_values = set()
    for member in cls:
        if member.value[0] in used_values:
            raise ValueError(f"Duplicate enum found - needs to be fixed by developer:  {member.value[0]}")
        used_values.add(member.value[0])
    return cls


class BaseMessage(Enum):
    """
        Base class for all the message enums. It provides the common format method for the messages.
    """

    def format(self, level, **kwargs):
        """
        It pre-pends PAIG-<log-level><error-code> to the message string
        :param level: log level
        :param kwargs: parameters to format the string
        :return: formatted string with PAIG-5x prefix
        """
        error_code = self.value[0]
        message_template = self.value[1]
        level_name = logging.getLevelName(level)
        return f'{level_name}: PAIG-{error_code}: {message_template.format(**kwargs)}'


@unique_message_enum
class ErrorMessage(BaseMessage):
    """
    Enum that has all the error messages. Do not change the order of the messages. Add new message to the end of the
    list always so that the order is not changed.
    """
    TENANT_ID_NOT_PROVIDED = 400001, "Tenant ID is not provided."
    API_KEY_NOT_PROVIDED = 400002, "Application config file not found. Cannot initialize Shield Plugin Library."
    PAIG_IS_ALREADY_INITIALIZED = 400003, "Shield Plugin is already initialized"
    PAIG_ACCESS_DENIED = 400004, "{server_error_message}"
    FRAMEWORKS_NOT_PROVIDED = 400005, "Frameworks are not provided. You should provide at least one framework such as " \
                                      "langchain. You can set to None if you do not want to intercept any framework."
    SHIELD_SERVER_KEY_ID_NOT_PROVIDED = 400006, "Shield server key id is not provided"
    SHIELD_SERVER_PUBLIC_KEY_NOT_PROVIDED = 400007, "Shield server public key is not provided"
    SHIELD_PLUGIN_KEY_ID_NOT_PROVIDED = 400008, "Shield plugin key id is not provided"
    SHIELD_PLUGIN_PRIVATE_KEY_NOT_PROVIDED = 400009, "Shield plugin private key is not provided"
    SHIELD_SERVER_INITIALIZATION_FAILED = 400010, "Shield server initialization request failed with status " \
                                                  "code={response_status}, body={response_data}"
    PROMPT_NOT_PROVIDED = 400011, "Prompt is not provided"
    CONVERSATION_TYPE_NOT_PROVIDED = 400012, "Conversation type is not provided"
    INVALID_APPLICATION_CONFIG_FILE = 400013, "Invalid application config file provided, error={error_message}"
    INVALID_APPLICATION_CONFIG_FILE_DATA = 400014, "application_config should be a dictionary or a string"
    APPLICATION_NOT_PROVIDED = 400015, "Application is not provided"
    APPLICATION_NOT_CONFIGURED = 400016, "Application failed to be configured"
    APP_CONFIG_FILE_IN_ENV_NOT_FOUND = 400017, "Application config file not found at {file_path} though it is set in " \
                                               "the environment variable"
    PARAMETERS_FOR_APP_CONFIG_NOT_PROVIDED = 400018, "Parameters for application config are not provided - you need " \
                                                     "to pass application_config_file or application_config"
    MULTIPLE_APP_CONFIG_FILES_FOUND = 400019, "Multiple application config files found at {file_path}"

    def format(self, **kwargs):
        return super().format(logging.ERROR, **kwargs)


@unique_message_enum
class InfoMessage(BaseMessage):
    """
    Enum that has all the info messages. Do not change the order of the messages. Add new message to the end of the
    list always so that the order is not changed.
    """
    PAIG_IS_INITIALIZED = 200001, "PAIGPlugin initialized with {kwargs}"
    LANGCHAIN_INITIALIZED = 200002, "Langchain setup done with {count} methods intercepted"
    NO_FRAMEWORKS_TO_INTERCEPT = 200003, "No frameworks to intercept"
    PRIVACERA_SHIELD_IS_ENABLED = 200004, "Privacera Shield, enabled={is_enabled}"
    USING_CONFIG_FILE_FROM_PARAMETER = 200005, "Using config file from {file_path} from parameter"
    USING_CONFIG_FILE_FROM_ENV_VAR = 200006, "Using config file from {file_path} from environment variable"
    USING_CONFIG_FILE_FROM_FOLDER = 200007, "Using config file from {file_path} from default folder"
    MILVUS_INITIALIZED = 200008, "Milvus setup done with {count} methods intercepted"
    LANGCHAIN_STREAMING_INITIALIZED = 200009, "Langchain Streaming setup done with {count} methods intercepted"
    OPENSEARCH_INITIALIZED = 200010, "OpenSearch setup done with {count} methods intercepted"

    def format(self, **kwargs):
        return super().format(logging.INFO, **kwargs)


@unique_message_enum
class WarningMessage(BaseMessage):
    """
    Enum that has all the warning messages. Do not change the order of the messages. Add new message to the end of the
    list always so that the order is not changed.
    """
    APP_CONFIG_FILE_NOT_FOUND_IN_PARAMETER = 300001, "Application config file not found at {file_path} though it is passed as a parameter"
    FRAMEWORK_NOT_SUPPORTED = 300002, "Framework {framework} is not supported"
    APP_CONFIG_FILE_NOT_FOUND_IN_ENV = 300003, "Application config file not found at {file_path} though it is set in the environment variable"
    APP_CONFIG_FILE_NOT_FOUND_NO_DEFAULT_FOLDER = 300004, "Application config file not found at {file_path} as default folder is not present"
    APP_CONFIG_FILE_NOT_FOUND_IN_DEFAULT_FOLDER = 300005, "Application config file not found at {file_path} though default folder is present but there is not config json file in it"

    def format(self, **kwargs):
        return super().format(logging.WARNING, **kwargs)
