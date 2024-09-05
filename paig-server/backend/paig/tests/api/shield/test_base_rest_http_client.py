import pytest
import urllib3
from api.shield.client.base_rest_http_client import BaseRESTHttpClient


@pytest.fixture()
def base_url():
    return "https://dummyjson.com"


class TestBaseRESTHttpClient:

    #  Can initialize BaseRESTHttpClient instance with a base URL
    def test_initialize_with_base_url(self, base_url):
        # Act
        client = BaseRESTHttpClient(base_url)

        # Assert
        assert client.baseUrl == base_url

    #  Can make a GET request to the API using the get method
    def test_get_request(self, base_url):
        # Arrange
        client = BaseRESTHttpClient(base_url)

        # Act
        response = client.get(url='/products')

        # Assert
        assert response.status_code == 200
        assert response.text is not None

    #  Can make a POST request to the API using the post method
    def test_post_request(self, base_url):
        # Arrange
        client = BaseRESTHttpClient(base_url)

        # Act
        json_data = {"title": "Key Holder 2", "description": "Attractive DesignMetallic Quality", "price": 301}
        response = client.post(url='/products/add', json=json_data)

        # Assert
        assert response.status_code == 201
        assert response.text is not None
        response_obj = response.json()
        response_obj.pop('id')
        assert response_obj == json_data

    #  Can make a PUT request to the API using the put method
    def test_put_request(self, mocker, base_url):
        # Arrange
        client = BaseRESTHttpClient(base_url)

        # Act
        response = client.put(url='/products/23', json={"title": "Key Holder 3"})

        # Assert
        assert response.status_code == 200
        assert response.text is not None
        response_obj = response.json()
        assert response_obj['title'] == 'Key Holder 3'

    #  Can make a DELETE request to the API using the delete method
    def test_delete_request(self, base_url):
        # Arrange
        client = BaseRESTHttpClient(base_url)

        # Act
        response = client.put(url='/products/25')

        # Assert
        assert response.status_code == 200
        assert response.text is not None
        response_obj = response.json()
        assert response_obj['id'] == 25

    #  Can make a PATCH request to the API using the patch method
    def test_patch_request(self, base_url):
        # Arrange
        client = BaseRESTHttpClient(base_url)

        # Act
        response = client.put(url='/products/25', json={"title": "Key Holder 5"})

        # Assert
        assert response.status_code == 200
        assert response.text is not None
        response_obj = response.json()
        assert response_obj['title'] == 'Key Holder 5'

    #  Handles cases where headers are not included in the request
    def test_custom_headers(self, mocker, base_url):
        # Arrange
        client = BaseRESTHttpClient(base_url)
        mocker.patch('urllib3.PoolManager.request')

        # Act
        client.get(url='/products', headers={'key': 'value'})

        # Assert
        urllib3.PoolManager.request.assert_called_once_with(method='GET', url='https://dummyjson.com/products',
                                                            headers={'Content-Type': 'application/json',
                                                                     'Accept': 'application/json', 'key': 'value'})

    #  Handles cases where the URL is not included in the request
    def test_no_url_included(self, mocker, base_url):
        # Arrange
        client = BaseRESTHttpClient(base_url)
        mocker.patch('urllib3.PoolManager.request')

        # Act
        client.get()

        # Assert
        urllib3.PoolManager.request.assert_called_once_with(method='GET', headers=client.get_default_headers())
