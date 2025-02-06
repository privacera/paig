import threading
import uuid

from sqlalchemy import func

from core.exceptions.error_messages_parser import get_error_message, ERROR_FIELD_REQUIRED, ERROR_FIELD_LENGTH_EXCEEDS, \
    ERROR_INVALID_STATUS, ERROR_FIELD_VALUE_INVALID
from .exceptions import BadRequestException

from datetime import datetime, timedelta
from pydantic import BaseModel
import os


def recursive_merge_dicts(dict1, dict2):
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = recursive_merge_dicts(result[key], value)
        else:
            result[key] = value

    return result


pwd_context = None


def get_or_create_pwd_context():
    global pwd_context
    if pwd_context is None:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context


def verify_password(plain_password, hashed_password):
    pwd_context = get_or_create_pwd_context()
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    pwd_context = get_or_create_pwd_context()
    return pwd_context.hash(password)


# Validation related functions
def validate_required_data(data, field_name):
    if not data:
        raise BadRequestException(get_error_message(ERROR_FIELD_REQUIRED, field_name))


def validate_string_data(data: str, field_name: str, required: bool = True, max_length: int = 255):
    if required:
        validate_required_data(data, field_name)
    else:
        if data and len(data) > max_length:
            raise BadRequestException(get_error_message(ERROR_FIELD_LENGTH_EXCEEDS, field_name, max_length))


def validate_id(id: int, field: str):
    if id is not None and id <= 0:
        raise BadRequestException(get_error_message(ERROR_FIELD_VALUE_INVALID, field, id))


def validate_boolean(status: int, field: str):
    if status:
        if status < 0 or status > 1:
            raise BadRequestException(get_error_message(ERROR_INVALID_STATUS, field, status))


def current_utc_time():
    import pytz
    return datetime.now().astimezone(pytz.utc)


def generate_unique_identifier_key():
    return str(uuid.uuid4())


def get_field_name_by_alias(model: BaseModel, alias: str) -> str:
    for field_name, field in model.model_fields.items():
        if field.alias == alias:
            return field_name
    return alias


def format_time_for_datetime_series(interval, start_time, end_time, db_datetime=None):
    offset_interval = '+1 ' + interval
    formatted_db_time = formatted_start_time = formatted_end_time = None
    if interval == 'month':
        if db_datetime is not None:
            formatted_db_time = func.strftime('%Y-%m-01', db_datetime)
        formatted_start_time = start_time.strftime('%Y-%m-01 00:00:00')
        formatted_end_time = end_time.strftime('%Y-%m-01 00:00:00')
    elif interval == 'year':
        if db_datetime is not None:
            formatted_db_time = func.strftime('%Y-01-01', db_datetime)
        formatted_start_time = start_time.strftime('%Y-01-01 00:00:00')
        formatted_end_time = end_time.strftime('%Y-01-01 00:00:00')
    elif interval == 'day':
        if db_datetime is not None:
            formatted_db_time = func.strftime('%Y-%m-%d', db_datetime)
        formatted_start_time = start_time.strftime('%Y-%m-%d 00:00:00')
        formatted_end_time = end_time.strftime('%Y-%m-%d 00:00:00')
    elif interval == 'hour':
        if db_datetime is not None:
            formatted_db_time = func.strftime('%Y-%m-%d %H:00:00', db_datetime)
        formatted_start_time = start_time.strftime('%Y-%m-%d %H:00:00')
        formatted_end_time = end_time.strftime('%Y-%m-%d %H:00:00')
    elif interval == 'week':
        if db_datetime is not None:
            formatted_db_time = func.date(func.strftime('%Y-%m-%d', db_datetime), '-6 day', 'weekday 1')
        formatted_start_time = get_start_of_week(start_time).strftime('%Y-%m-%d 00:00:00')
        formatted_end_time = get_start_of_week(end_time).strftime('%Y-%m-%d 00:00:00')
        offset_interval = '+7 day'
    return offset_interval, formatted_start_time, formatted_end_time, formatted_db_time


def get_start_of_week(date):
    # Calculate the start of the week (Monday)
    start = date - timedelta(days=date.weekday())
    return start


def get_current_server_ip():
    import socket
    try:
        # Create a temporary socket to determine the IP address
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a non-routable address (won't actually send data)
        temp_socket.connect(("10.254.254.254", 1))
        # Retrieve the local IP address assigned to the socket
        ip_address = temp_socket.getsockname()[0]
        # Close the socket
        temp_socket.close()
        return ip_address
    except Exception as e:
        return f"Error retrieving IP address: {e}"


def format_to_root_path(path):
    path_append = ""
    if os.getenv('PAIG_ROOT_DIR'):
        path_append = os.getenv('PAIG_ROOT_DIR') + '/'
    return f"{path_append}{path}"


def get_interval(from_time, to_time):
    from_time_dt = datetime.utcfromtimestamp(from_time / 1000)
    to_time_dt = datetime.utcfromtimestamp(to_time / 1000)

    days = (to_time_dt - from_time_dt).days

    if days <= 2:
        return "hour"
    elif 2 < days < 7:
        return "day"
    elif 30 > days > 7:
        return "day"
    elif 60 > days > 30:
        return "week"
    elif 365 > days > 60:
        return "month"
    elif days > 365:
        return "quarter"
    else:
        return "month"


def acquire_lock(lock_file_path):
    import fasteners
    lock = fasteners.InterProcessLock(lock_file_path)
    gotten = None
    if lock_file_path:
        try:
            gotten = lock.acquire(blocking=False)
        except threading.ThreadError:
            pass
    return lock if gotten else None


class Singleton:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__new__(cls)
        return cls._instances[cls]

    def is_instance_initialized(self):
        if hasattr(self, '_initialized') and self._initialized:
            return True
        else:
            self._initialized = True
            return False


global_instances = {}


def SingletonDepends(dependency, called_inside_fastapi_depends=False):
    if dependency not in global_instances:
        global_instances[dependency] = dependency()

    if called_inside_fastapi_depends:
        def callable():
            return global_instances[dependency]

        return callable

    else:
        return global_instances[dependency]


def snake_to_camel(snake_str):
    components = snake_str.split('_')
    # Capitalize the first letter of each component except the first one and join them together
    return components[0] + ''.join(x.title() for x in components[1:])


def detect_environment():
    if is_jupyter_notebook():
        return 'jupyter'
    elif is_colab():
        return 'colab'
    elif is_docker():
        return 'docker'
    else:
        return 'local'


def is_jupyter_notebook():
    try:
        from IPython import get_ipython
        # Check if IPython is available and running in a notebook environment
        ipython = get_ipython()
        if ipython is None:
            return False
        return 'IPKernelApp' in ipython.config.get('IPKernelApp', {})
    except:
        return False


def is_colab():
    try:
        import google.colab
    except ImportError:
        return False
    try:
        from IPython.core.getipython import get_ipython
    except ImportError:
        return False
    return True


def is_docker():
    return os.path.exists('/.dockerenv')
