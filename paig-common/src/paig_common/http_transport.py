import urllib3
import threading
from urllib3 import Timeout, Retry


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
                HttpTransport._http = urllib3.PoolManager(num_pools=50, block=True, retries=retries, timeout=timeout)
