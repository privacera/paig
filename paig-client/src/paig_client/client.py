from . import core


def setup(**kwargs):
    """Initializes an instance of the Shield library. This method should be called only once.
    It can also detect an AI application config file in following ways:
        1. If the environment variable PRIVACERA_SHIELD_CONF_FILE is set, then it will use the file path specified in
        the environment variable.
        2. If the application_config_file parameter is set, then it will use the file path specified in the parameter.
        3. If the application_config parameter is set, then it will use the contents of the parameter. If it is a
        string, then it will treat it as the contents of the file. If it is a dictionary, then it
        will use the dictionary as the application config.
        4. If the application_config parameter is not set, then it will look for a file that matches the pattern
        'privacera-shield-*-config.json' in either a folder named privacera or folder pointed to
        by PRIVACERA_SHIELD_CONF_DIR environment variable. The folder should contain only one file.

    Args:
        kwargs: The name-value pairs to be set in the context. The following are the supported options:

            enable_privacera_shield (bool): Whether to enable Privacera Shield. Default is True.

            frameworks (list): The list of frameworks to intercept methods from. This is mandatory. You
            can set this to ['None'] if you do not want to intercept any framework.

            application_config_file (str): The path to the application config file. This is optional.

            application_config (str or dict): The contents of the application config file. This is optional.

            http: An instance of urlib3.PoolManager to be used by the PAIG plugin. This is optional.

            max_retries (int): The maximum number of retries for HTTP requests. This is optional.

            backoff_factor (int): The backoff factor for HTTP retries. This is optional.

            allowed_methods (list): The list of HTTP methods allowed for retry. This is optional.

            status_retry_forcelist (list): The list of HTTP status codes for which retry is forced. This is optional.

            connection_timeout (float): The connection timeout for the access request. This is optional.

            read_timeout (float): The read timeout for the access request. This is optional.
    """
    core.setup(**kwargs)


def create_shield_context(**kwargs):
    """Create a context manager for the PAIG plugin. Now you can write code such as -

    with create_shield_context(username="user1"):
        response_text = check_access(text="hello world", conversation_type=ConversationType.PROMPT)
        print(response_text)

    Args:
        kwargs:

    Returns:
        A context manager for the PAIG plugin.
    """
    return core.create_shield_context(**kwargs)


def set_current_user(username):
    """
    Set the current user_name context for the PAIG plugin.

    Args:
        username (str): The username of the current user_name.
    """
    core.set_current_user(username)  # Set the current user_name


def set_current(**kwargs):
    """
    Set the list of name-value pairs from kwargs into the thread-local context for the PAIG plugin.
    Args:
        kwargs:
    """
    core.set_current(**kwargs)


def get_current_user():
    """
    Get the current user_name context for the PAIG plugin.
    Returns:
        The username of the current user_name from the context.
    """
    return core.get_current("username")


def get_current(key, default_value=None):
    """
    Get the value of the given key from the thread-local context for the PAIG plugin.
    Args:
        key: the key
        default_value: the default value to be returned if the key is not found in the context.
    Returns:
        The value of the given key from the context.
    """
    return core.get_current(key, default_value)


def clear():
    """
    Clear the thread-local context for the PAIG plugin.
    """
    core.clear()


def check_access(**kwargs):
    """
    Check access for the given text.
    Args:
        kwargs: The name-value pairs to be set in the context. The following are the supported options:

            text (str or [str]): The text to be checked for access.

            conversation_type (ConversationType): The type of conversation. This is mandatory.
    Returns:
        A list of ResponseText objects.
    """
    return core.check_access(**kwargs)


def get_vector_db_filter_expression(**kwargs):
    """
    Check vector db filter expression for current user
    Args:
        kwargs: The name-value pairs to be set in the context.
    Returns:
        A filter expression
    """
    return core.get_vector_db_filter_expression(**kwargs)


def dummy_access_denied():
    """
    Raise an AccessDenied exception. This method can be used to test AccessDenied exception handling.
    """
    core.dummy_access_denied()


def setup_app(**kwargs):
    """
    Creates an instance of the AI application based on the application config file. This method should be
    used when you have multiple AI applications in the same process.
    Args:
        kwargs: The name-value pairs to be set in the context. The following are the supported options:
            application_config_file (str): The path to the application config file. This is optional.

            application_config (str or dict): The contents of the application config file. This is optional.

    Returns:
        An object that you should pass in the context manager
    """
    return core.setup_app(**kwargs)
