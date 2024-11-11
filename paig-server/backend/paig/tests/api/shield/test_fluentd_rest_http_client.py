from api.shield.client.http_fluentd_client import FluentdRestHttpClient
import pytest

from api.shield.utils.custom_exceptions import ShieldException


class TestFluentdRestHttpClient:

    #  Able to log a message successfully
    def test_able_to_log_message_successfully(self, mocker):
        # Arrange
        message = "Test message"
        response_mock = mocker.Mock()
        response_mock.status_code = 200

        side_effect = lambda prop, default=None: {
            'fluentd_base_url': 'http://localhost:9880',
            'fluentd_tag': 'audit_tag',
            'paig_api_key': '1234567890'
        }.get(prop, default)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        fluentd_client = FluentdRestHttpClient()
        fluentd_client.post = mocker.Mock(return_value=response_mock)

        # Act
        fluentd_client.log_message(message)

        # Assert
        fluentd_client.post.assert_called_once_with(url="/audit_tag", headers=fluentd_client.get_headers(),
                                                    json=message)

    #  Able to log a message with empty headers
    def test_able_to_log_message_with_empty_headers(self, mocker):
        # Arrange
        message = "Test message"
        response_mock = mocker.Mock()
        response_mock.status_code = 200

        side_effect = lambda prop, default=None: {
            'fluentd_base_url': 'http://localhost:9880',
            'fluentd_tag': 'audit_tag',
        }.get(prop, default)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        fluentd_client = FluentdRestHttpClient()
        fluentd_client.post = mocker.Mock(return_value=response_mock)

        # Act
        fluentd_client.log_message(message)

        # Assert
        fluentd_client.post.assert_called_once_with(url="/audit_tag", headers={}, json=message)

    #  Unable to log a message due to network error
    def test_unable_to_log_message_due_to_network_error(self, mocker):
        # Arrange
        message = "Test message"

        side_effect = lambda prop, default=None: {
            'fluentd_base_url': 'http://localhost:9880',
            'fluentd_tag': 'audit_tag',
        }.get(prop, default)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        fluentd_client = FluentdRestHttpClient()
        fluentd_client.post = mocker.Mock(side_effect=Exception("Network error"))

        # Act
        with pytest.raises(ShieldException):
            fluentd_client.log_message(message)

        # Assert
        fluentd_client.post.assert_called_once_with(url="/audit_tag", headers=fluentd_client.get_headers(),
                                                    json=message)

    #  Unable to log a message due to server error
    def test_unable_to_log_message_due_to_server_error(self, mocker):
        # Arrange
        message = "Test message"
        response_mock = mocker.Mock()
        response_mock.status_code = 500

        side_effect = lambda prop, default=None: {
            'fluentd_base_url': 'http://localhost:9880',
            'fluentd_tag': 'audit_tag',
        }.get(prop, default)

        mocker.patch('api.shield.utils.config_utils.get_property_value', side_effect=side_effect)

        fluentd_client = FluentdRestHttpClient()
        fluentd_client.post = mocker.Mock(return_value=response_mock)

        # Act
        with pytest.raises(ShieldException):
            fluentd_client.log_message(message)

        # Assert
        fluentd_client.post.assert_called_once_with(url="/audit_tag", headers=fluentd_client.get_headers(),
                                                    json=message)

    #  Unable to log a message due to invalid base URL
    def test_unable_to_log_message_due_to_invalid_base_url(self):
        # Arrange
        message = "Test message"
        fluentd_client = FluentdRestHttpClient()
        fluentd_client.baseUrl = None

        # Act
        with pytest.raises(ShieldException):
            fluentd_client.log_message(message)


