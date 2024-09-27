import logging
import socket
import threading

from datetime import datetime, timezone
from functools import lru_cache

_logger = logging.getLogger(__name__)


def get_time_now_utc():
    utc_dt = datetime.now(timezone.utc)
    return utc_dt


def get_time_now_utc_str():
    """
    Get current time in UTC in ISO 8601 format compatible with Java
    :return: str
    """
    utc_dt = datetime.now(timezone.utc)
    utc_dt_str = get_time_now_utc().strftime('%Y-%m-%dT%H:%M:%S') + utc_dt.strftime('.%f')[:4] + utc_dt.strftime('Z')
    return utc_dt_str


def get_time_from_isotime(utc_dt_str):
    return datetime.fromisoformat(utc_dt_str)


@lru_cache(maxsize=None)
def get_my_hostname():
    return socket.gethostname()


@lru_cache(maxsize=None)
def get_my_ip_address():
    ip_address = ""

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
    except Exception:
        _logger.exception("Not able to retrieve host ip address")

    return ip_address


class AtomicCounter:
    def __init__(self, initial=0):
        self.value = initial
        self._lock = threading.Lock()
        self.max_limit = 2 ** 15 - 1

    def increment(self, offset=1):
        with self._lock:
            self.value = (self.value + offset) % self.max_limit
            return self.value


def process_nested_input(input, output_list, extract=True):
    """
    Extracts all the text from the input and stores it in the output_list. If extract is False, then it replaces the
    text in the input with the text from the output_list.
    :param input: dict or list
    :param output_list: list
    :param extract: if True then extract the text from input and store it in output_list, else replace the text in
    input with the text from output_list
    :return:
    """
    if isinstance(input, dict):
        for key in sorted(input.keys()):
            value = input[key]
            if isinstance(value, str):
                if extract:
                    output_list.append(value)
                else:
                    input[key] = output_list.pop()
            elif isinstance(value, list):
                process_nested_input(value, output_list)
    elif isinstance(input, list):
        for index, item in enumerate(input):
            if isinstance(item, str):
                if extract:
                    output_list.append(item)
                else:
                    input[index] = output_list.pop()
            elif isinstance(item, dict):
                process_nested_input(item, output_list)
