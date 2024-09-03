import urllib3

from paig_common.http_transport import HttpTransport


class TestHttpTransport:

    #  HttpTransport.get_http() returns an instance of urllib3.PoolManager
    def test_get_http_returns_instance_of_pool_manager(self):
        # Invoke the method under test
        http = HttpTransport.get_http()

        # Assert that the method returns an instance of urllib3.PoolManager
        assert isinstance(http, urllib3.PoolManager)

    #  HttpTransport.create_default_http() creates a default instance of urllib3.PoolManager
    def test_create_default_http_creates_default_instance_of_pool_manager(self):
        # Invoke the method under test
        HttpTransport.create_default_http()
        retries = urllib3.Retry(total=4,
                                backoff_factor=1,
                                allowed_methods=["GET", "POST", "PUT", "DELETE"],
                                status_forcelist=[500, 502, 503, 504])
        timeout = urllib3.Timeout(connect=2.0, read=7.0)
        # Assert that the PoolManager constructor is called with the correct arguments
        assert HttpTransport._http.connection_pool_kw.get('block') == True
        assert compare_objects(HttpTransport._http.connection_pool_kw.get('retries'), retries)
        assert compare_objects(HttpTransport._http.connection_pool_kw.get('timeout'), timeout)

    #  HttpTransport.setup() allows overriding default settings
    def test_setup_allows_overriding_default_settings(self):
        # Invoke the method under test
        HttpTransport.setup(max_retries=3, backoff_factor=2, allowed_methods=["GET"], status_forcelist=[500])

        # Assert that the default settings are overridden
        assert HttpTransport._max_retries == 3
        assert HttpTransport._backoff_factor == 2
        assert HttpTransport._allowed_methods == ["GET"]
        assert HttpTransport._status_forcelist == [500]


def compare_objects(obj1, obj2):
    # Check if the objects are of the same type
    if type(obj1) != type(obj2):
        return False

    # Get the dictionary of attributes for each object
    attrs1 = vars(obj1)
    attrs2 = vars(obj2)

    # Compare attributes
    for key in attrs1.keys():
        if attrs1[key] != attrs2.get(key):
            return False

    return True
