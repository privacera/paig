import httpx
import asyncio
import logging

from . import config_utils

logger = logging.getLogger(__name__)


class AsyncHttpTransport:
    """
    AsyncHttpTransport class maintains a single instance of httpx.AsyncClient for all the AsyncShieldRestHttpClient instances.
    """
    _client: httpx.AsyncClient = None
    _lock = asyncio.Lock()
    _connect_timeout_sec = 2.0
    _read_timeout_sec = 7.0
    """
    These are default settings that can be overridden by calling the setup method.
    """

    @staticmethod
    async def setup(**kwargs):
        """
        This optional method allows you to pass your own settings to be used by all the
        AsyncShieldRestHttpClient instances.
        :param kwargs:
            - connect_timeout_sec
            - read_timeout_sec
        :return:
        """
        AsyncHttpTransport._connect_timeout_sec = kwargs.get('connect_timeout_sec',
                                                             AsyncHttpTransport._connect_timeout_sec)
        AsyncHttpTransport._read_timeout_sec = kwargs.get('read_timeout_sec', AsyncHttpTransport._read_timeout_sec)

        await AsyncHttpTransport.create_default_client()

    @staticmethod
    async def get_client():
        if not AsyncHttpTransport._client:
            await AsyncHttpTransport.create_default_client()
        return AsyncHttpTransport._client

    @staticmethod
    async def create_default_client():
        async with AsyncHttpTransport._lock:
            if not AsyncHttpTransport._client:

                timeout = httpx.Timeout(
                    connect=AsyncHttpTransport._connect_timeout_sec,
                    read=AsyncHttpTransport._read_timeout_sec,
                    write=None,
                    pool=None
                )
                max_keepalive_connections = config_utils.get_property_value_int("httpx.rest.client.max.keepalive.connections", 50)
                max_connections = config_utils.get_property_value_int("httpx.rest.client.max.connections", 100)
                keepalive_expiry = config_utils.get_property_value_float("httpx.rest.client.keep.alive.expiry", 60.0)
                limits = httpx.Limits(max_keepalive_connections=max_keepalive_connections, max_connections=max_connections, keepalive_expiry=keepalive_expiry)
                transport = httpx.AsyncHTTPTransport(limits=limits)

                AsyncHttpTransport._client = httpx.AsyncClient(
                    timeout=timeout,
                    transport=transport
                )

    @staticmethod
    async def close():
        """
        Close the httpx AsyncClient.
        """
        if AsyncHttpTransport._client:
            await AsyncHttpTransport._client.aclose()
            AsyncHttpTransport._client = None
