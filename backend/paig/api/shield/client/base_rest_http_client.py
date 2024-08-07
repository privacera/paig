from typing import Collection

from privacera_shield_common.http_transport import HttpTransport
from api.shield.utils import config_utils
from urllib3.response import HTTPResponse
import json


class BaseRESTHttpClient:
    """
    A base class for making HTTP requests to a RESTful API.
    """

    def __init__(self, base_url):
        """
        Initialize the BaseRESTHttpClient instance.

        Args:
            base_url (str): The base URL of the REST API.
        """
        self.baseUrl = base_url
        self.setup()

    def setup(self):
        """
        Setup the HTTP transport configuration.

        Returns:
        None
        """
        max_retries = config_utils.get_property_value_int("http.rest.client.max_retries", 4)
        backoff_factor = config_utils.get_property_value_int("http.rest.client.backoff_factor", 1)
        allowed_methods_str = config_utils.get_property_value("http.rest.client.allowed_methods", '["GET", "POST", "PUT", "DELETE"]')
        allowed_methods: Collection[str] = eval(allowed_methods_str)
        status_forcelist_str = config_utils.get_property_value("http.rest.client.status_forcelist", '[500, 502, 503, 504]')
        status_forcelist: Collection[int] = eval(status_forcelist_str)
        connect_timeout_sec = config_utils.get_property_value_float("http.rest.client.connect_timeout_sec", 2.0)
        read_timeout_sec = config_utils.get_property_value_float("http.rest.client.read_timeout_sec", 7.0)
        HttpTransport.setup(max_retries=max_retries, backoff_factor=backoff_factor, allowed_methods=allowed_methods,
                            status_forcelist=status_forcelist, connect_timeout_sec=connect_timeout_sec,
                            read_timeout_sec=read_timeout_sec)

    def get_auth(self):
        """
        Get the authentication configuration for the HTTP requests.

        Returns:
            None or tuple: None if no authentication is needed, a tuple (username, password) otherwise.
        """
        return None

    def get_default_headers(self):
        """
        Get the default HTTP headers to include in each request.

        Returns:
            dict: A dictionary containing default headers.
        """
        return {"Content-Type": "application/json", "Accept": "application/json"}

    def request(self, *args, **kwargs):
        """
        Make an HTTP request to the API.

        Args:
            *args: Positional arguments for the request method.
            **kwargs: Keyword arguments for the request.

        Returns:
            requests.Response: The HTTP response object.
        """
        headers = {}

        if "headers" in kwargs:
            headers = kwargs["headers"]

        if "url" in kwargs:
            kwargs["url"] = self.baseUrl + kwargs["url"]

        updated_headers = self.get_default_headers()
        updated_headers.update(headers)
        kwargs["headers"] = updated_headers

        auth = self.get_auth()

        if auth is not None:
            http_response = HttpTransport.get_http().request(*args, auth=auth, **kwargs)
        else:
            http_response = HttpTransport.get_http().request(*args, **kwargs)

        return ReturnValue(http_response)

    def get(self, *args, **kwargs):
        """
        Make a GET request to the API.

        Args:
            *args: Positional arguments for the request method.
            **kwargs: Keyword arguments for the request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self.request(method='GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        """
        Make a POST request to the API.

        Args:
            *args: Positional arguments for the request method.
            **kwargs: Keyword arguments for the request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self.request(method='POST', *args, **kwargs)

    def put(self, *args, **kwargs):
        """
        Make a PUT request to the API.

        Args:
            *args: Positional arguments for the request method.
            **kwargs: Keyword arguments for the request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self.request(method='PUT', *args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Make a DELETE request to the API.

        Args:
            *args: Positional arguments for the request method.
            **kwargs: Keyword arguments for the request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self.request(method='DELETE', *args, **kwargs)

    def patch(self, *args, **kwargs):
        """
        Make a PATCH request to the API.

        Args:
            *args: Positional arguments for the request method.
            **kwargs: Keyword arguments for the request.

        Returns:
            requests.Response: The HTTP response object.
        """
        return self.request(method='PATCH', *args, **kwargs)


class ReturnValue:
    def __init__(self, response: HTTPResponse = None):
        self.status_code = response.status
        self.text = response.data.decode("utf-8")

    def json(self):
        return json.loads(self.text)

    def __str__(self):
        return f"Response return value: (status_code={self.status_code}, text={self.text})"
