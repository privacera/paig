import unittest

from unittest.mock import patch

from api.guardrails.providers import GuardrailConnection, GuardrailProviderManager, GuardrailProvider, \
    CreateGuardrailRequest, UpdateGuardrailRequest, DeleteGuardrailRequest, GuardrailConfig


# Mocked GuardrailProvider Implementation for Testing
class MockGuardrailProvider(GuardrailProvider):
    def verify_connection_details(self, **kwargs):
        return True, {"message": "Verified successfully"}

    def create_guardrail(self, request, **kwargs):
        return True, {"message": "Guardrail created successfully"}

    def update_guardrail(self, request, **kwargs):
        return True, {"message": "Guardrail updated successfully"}

    def delete_guardrail(self, request, **kwargs):
        return True, {"message": "Guardrail deleted successfully"}


class TestGuardrailProviderManager(unittest.TestCase):

    @patch("api.guardrails.providers.GuardrailProviderManager._get_provider_instance")
    def test_verify_guardrails_connection_details(self, mock_get_provider):
        # Mocking
        mock_provider_instance = MockGuardrailProvider(connection_details={})
        mock_get_provider.return_value = mock_provider_instance

        # Input
        connection_request = {
            "AWS": GuardrailConnection(
                name="test-connection",
                description="test-description",
                guardrailProvider="AWS",
                connectionDetails={"region": "us-east-1"}
            ),
        }

        # Call
        result = GuardrailProviderManager.verify_guardrails_connection_details(connection_request)

        # Assert
        self.assertEqual(result["AWS"]["success"], True)
        self.assertEqual(result["AWS"]["response"]["message"], "Verified successfully")

    @patch("api.guardrails.providers.GuardrailProviderManager._get_provider_instance")
    def test_create_guardrail(self, mock_get_provider):
        # Mocking
        mock_provider_instance = MockGuardrailProvider(connection_details={})
        mock_get_provider.return_value = mock_provider_instance

        # Input
        create_request = {
            "AWS": CreateGuardrailRequest(
                name="test-guardrail",
                description="test-description",
                connectionDetails={"region": "us-east-1"},
                guardrailConfigs=[GuardrailConfig(status=1, guardrailProvider="AWS",
                        configType="topicPolicyConfig", configData={})]
            ),
        }

        # Call
        result = GuardrailProviderManager.create_guardrail(create_request)

        # Assert
        self.assertEqual(result["AWS"]["success"], True)
        self.assertEqual(result["AWS"]["response"]["message"], "Guardrail created successfully")

    @patch("api.guardrails.providers.GuardrailProviderManager._get_provider_instance")
    def test_update_guardrail(self, mock_get_provider):
        # Mocking
        mock_provider_instance = MockGuardrailProvider(connection_details={})
        mock_get_provider.return_value = mock_provider_instance

        # Input
        update_request = {
            "AWS": UpdateGuardrailRequest(
                name="test-guardrail",
                description="test-description",
                connectionDetails={"region": "us-east-1"},
                guardrailConfigs=[GuardrailConfig(status=1, guardrailProvider="AWS",
                        configType="topicPolicyConfig", configData={})],
                remoteGuardrailDetails={},
            ),
        }

        # Call
        result = GuardrailProviderManager.update_guardrail(update_request)

        # Assert
        self.assertEqual(result["AWS"]["success"], True)
        self.assertEqual(result["AWS"]["response"]["message"], "Guardrail updated successfully")

    @patch("api.guardrails.providers.GuardrailProviderManager._get_provider_instance")
    def test_delete_guardrail(self, mock_get_provider):
        # Mocking
        mock_provider_instance = MockGuardrailProvider(connection_details={})
        mock_get_provider.return_value = mock_provider_instance

        # Input
        delete_request = {
            "AWS": DeleteGuardrailRequest(
                name="test-guardrail",
                description="test-description",
                connectionDetails={"region": "us-east-1"},
                guardrailConfigs=[GuardrailConfig(status=1, guardrailProvider="AWS",
                        configType="topicPolicyConfig", configData={})],
                remoteGuardrailDetails={},
            ),
        }

        # Call
        result = GuardrailProviderManager.delete_guardrail(delete_request)

        # Assert
        self.assertEqual(result["AWS"]["success"], True)
        self.assertEqual(result["AWS"]["response"]["message"], "Guardrail deleted successfully")