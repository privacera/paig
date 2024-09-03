import asyncio
import json
from typing import Collection
import httpx

from . import config_utils
from .async_http_transport import AsyncHttpTransport
import logging

logger = logging.getLogger(__name__)


class AsyncBaseRESTHttpClient:
    """
    An asynchronous base class for making HTTP requests to a RESTful API using httpx.
    """
    _setup_done = False  # Flag to track if setup has been performed
    _setup_lock = asyncio.Lock()
    _max_retries = config_utils.get_property_value_int("http.rest.client.max_retries", 4)
    _backoff_factor = config_utils.get_property_value_int("http.rest.client.backoff_factor", 1)
    _allowed_methods_str = config_utils.get_property_value("http.rest.client.allowed_methods",
                                                           '["GET", "POST", "PUT", "DELETE"]')
    _allowed_methods: Collection[str] = eval(_allowed_methods_str)
    _status_forcelist_str = config_utils.get_property_value("http.rest.client.status_forcelist",
                                                            '[500, 502, 503, 504]')
    _status_forcelist: Collection[int] = eval(_status_forcelist_str)

    def __init__(self, base_url):
        """
        Initialize the AsyncBaseRESTHttpClient instance.

        Args:
            base_url (str): The base URL of the REST API.
        """
        self.baseUrl = base_url

    @staticmethod
    async def setup():
        """
        Set up the Async HTTP transport configuration (called only once).

        Returns:
        None
        """
        async with AsyncBaseRESTHttpClient._setup_lock:
            if not AsyncBaseRESTHttpClient._setup_done:
                connect_timeout_sec = config_utils.get_property_value_float("http.rest.client.connect_timeout_sec", 2.0)
                read_timeout_sec = config_utils.get_property_value_float("http.rest.client.read_timeout_sec", 7.0)
                await AsyncHttpTransport.setup(
                    connect_timeout_sec=connect_timeout_sec,
                    read_timeout_sec=read_timeout_sec
                )
                AsyncBaseRESTHttpClient._setup_done = True

    def get_auth(self):
        """
        Get the authentication configuration for the HTTP requests.

        Returns:
            None or httpx.Auth: None if no authentication is needed, an httpx.Auth object otherwise.
        """
        return None

    def get_default_headers(self):
        """
        Get the default HTTP headers to include in each request.

        Returns:
            dict: A dictionary containing default headers.
        """
        return {"Content-Type": "application/json", "Accept": "application/json"}

    async def request(self, *args, **kwargs):
        """
        Make an asynchronous HTTP request to the API.

        Args:
            *args: Positional arguments for the request method.
            **kwargs: Keyword arguments for the request.

        Returns:
            AsyncReturnValue: The HTTP response object.
        """
        headers = kwargs.get("headers", {})

        if "url" in kwargs:
            kwargs["url"] = self.baseUrl + kwargs["url"]

        updated_headers = self.get_default_headers()
        updated_headers.update(headers)
        kwargs["headers"] = updated_headers

        auth = self.get_auth()
        if auth is not None:
            kwargs["auth"] = auth

        await AsyncBaseRESTHttpClient.setup()
        client = await AsyncHttpTransport.get_client()
        retries = AsyncBaseRESTHttpClient._max_retries
        backoff_factor = AsyncBaseRESTHttpClient._backoff_factor

        for attempt in range(retries + 1):
            try:
                response = await client.request(*args, auth=auth, **kwargs)
                if response.status_code not in AsyncBaseRESTHttpClient._status_forcelist:
                    return AsyncReturnValue(response)
            except httpx.RequestError as exc:
                if attempt == retries:
                    # Log error and raise exception after max retries
                    logger.error(f"Max retries reached without a successful response getting this exception: {exc}")
                    raise httpx.RequestError(
                        f"Max retries reached without a successful response getting this exception: {exc}")
                # Wait before retrying
                await asyncio.sleep(backoff_factor * (2 ** attempt))

    async def get(self, *args, **kwargs):
        return await self.request(method='GET', *args, **kwargs)

    async def post(self, *args, **kwargs):
        return await self.request(method='POST', *args, **kwargs)

    async def put(self, *args, **kwargs):
        return await self.request(method='PUT', *args, **kwargs)

    async def delete(self, *args, **kwargs):
        return await self.request(method='DELETE', *args, **kwargs)

    async def patch(self, *args, **kwargs):
        return await self.request(method='PATCH', *args, **kwargs)


class AsyncReturnValue:
    def __init__(self, response: httpx.Response):
        self.status_code = response.status_code
        self.text = response.text

    def json(self):
        return json.loads(self.text)

    def __str__(self):
        return f"Response return value: (status_code={self.status_code}, text={self.text})"
