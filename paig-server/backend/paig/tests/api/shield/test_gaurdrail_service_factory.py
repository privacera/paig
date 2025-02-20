import unittest
from unittest.mock import patch, MagicMock
from api.shield.utils import config_utils
from api.shield.factory.guardrail_service_factory import GuardrailServiceFactory


class TestGuardrailServiceFactory(unittest.TestCase):

    @patch.object(config_utils, 'get_property_value')
    def test_get_guardrail_service_client_http(self, mock_get_property_value):
        mock_get_property_value.return_value = "http"

        with patch('api.shield.client.http_guardrail_service_client.HttpGuardrailServiceClient') as mock_http_client:
            mock_http_client.return_value = MagicMock()
            factory = GuardrailServiceFactory()
            client = factory.get_guardrail_service_client()
            mock_http_client.assert_called_once()
            self.assertIsInstance(client, MagicMock)

    @patch.object(config_utils, 'get_property_value')
    def test_get_guardrail_service_client_local(self, mock_get_property_value):
        mock_get_property_value.return_value = "local"

        with patch('api.shield.client.local_guardrail_service_client.LocalGuardrailServiceClient') as mock_local_client:
            mock_local_client.return_value = MagicMock()
            factory = GuardrailServiceFactory()
            client = factory.get_guardrail_service_client()
            mock_local_client.assert_called_once()
            self.assertIsInstance(client, MagicMock)

    @patch.object(config_utils, 'get_property_value')
    def test_get_guardrail_service_client_invalid(self, mock_get_property_value):
        mock_get_property_value.return_value = "invalid_type"

        factory = GuardrailServiceFactory()
        with self.assertRaises(Exception) as context:
            factory.get_guardrail_service_client()

        self.assertEqual(str(context.exception),
                         "Invalid service type: 'invalid_type'. Expected 'http' or 'local'. "
                         "Please configure the 'guardrail_service_client' property with a valid service type.")