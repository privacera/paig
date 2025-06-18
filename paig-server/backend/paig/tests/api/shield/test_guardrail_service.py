import unittest, pytest
from unittest.mock import patch, AsyncMock, MagicMock

from presidio_analyzer import RecognizerResult
from api.shield.services.guardrail_service import (
    process_guardrail_response, get_guardrail_by_id, decrypted_connection_details, paig_pii_guardrail_evaluation, mask_message, merge_scanner_results,
    paig_guardrail_test, aws_guardrail_test, do_test_guardrail
)
from api.shield.model.scanner_result import ScannerResult

class TestGuardrailService(unittest.TestCase):

    def test_process_guardrail_response_with_valid_input(self):
        input_data = {
            "guardrail_configs": [
                {
                    "config_type": "SENSITIVE_DATA",
                    "config_data": {
                        "configs": [
                            {"category": "PII", "action": "DENY"},
                            {"category": "regex", "name": "EMAIL", "action": "REDACT"}
                        ]
                    },
                    "response_message": "Sensitive data found"
                },
                {
                    "config_type": "DENIED_TERMS",
                    "config_data": {
                        "configs": [
                            {"keywords": ["bad", "evil"], "action": "DENY"}
                        ]
                    },
                    "response_message": "Bad terms found"
                }
            ],
            "guardrail_provider_response": {
                "AWS": {
                    "response": {
                        "guardrailId": "123",
                        "guardrailArn": "arn:aws:guardrail:123",
                        "version": "1.0"
                    }
                }
            },
            "guardrail_connection_details": {
                "region": "us-east-1"
            }
        }
        expected_result = {
            "config_type": {
                "SENSITIVE_DATA": {
                    "configs": {
                        "PII": "DENY",
                        "EMAIL": "REDACT"
                    },
                    "response_message": "Sensitive data found"
                },
                "DENIED_TERMS": {
                    "configs": {
                        "bad": "DENY",
                        "evil": "DENY"
                    },
                    "response_message": "Bad terms found"
                }
            },
            "guardrail_provider_details": {
                "AWS": {
                    "guardrailId": "123",
                    "guardrailArn": "arn:aws:guardrail:123",
                    "version": "1.0",
                    "connection_details": {
                        "region": "us-east-1"
                    }
                }
            }
        }
        result = process_guardrail_response(input_data)
        self.assertEqual(result, expected_result)

    @patch('api.shield.services.guardrail_service.guardrail_service_client.get_guardrail_info_by_id')
    async def test_get_guardrail_by_id_with_valid_request(self, mock_get_guardrail_info_by_id):
        request = {"guardrailId": "123"}
        tenant_id = "tenant_1"
        mock_get_guardrail_info_by_id.return_value = {"guardrailId": "123", "details": "some details"}
        result = await get_guardrail_by_id(request, tenant_id)
        self.assertEqual(result, {"guardrailId": "123", "details": "some details"})
        mock_get_guardrail_info_by_id.assert_called_once_with(tenant_id, "123")

    @patch('api.shield.services.guardrail_service.TenantDataEncryptorService.decrypt_guardrail_connection_details')
    async def test_decrypted_connection_details_with_valid_details(self, mock_decrypt_guardrail_connection_details):
        tenant_id = "tenant_1"
        connection_details = {"region": "us-east-1"}
        await decrypted_connection_details(tenant_id, connection_details)
        mock_decrypt_guardrail_connection_details.assert_called_once_with(tenant_id, connection_details)

    def test_paig_pii_guardrail_evaluation_with_sensitive_data(self):
        sensitive_data_config = {"configs": {"PII": "DENY", "EMAIL": "REDACT"}}
        traits = ["PII", "EMAIL"]
        deny_policies_list, redact_policies_dict, []= paig_pii_guardrail_evaluation(sensitive_data_config, traits)
        self.assertEqual(deny_policies_list, ["PII"])
        self.assertEqual(redact_policies_dict, {"EMAIL": "<<EMAIL>>"})

    def test_mask_message_with_redact_policies(self):
        message = "My email is test@example.com"
        redact_policies_dict = {"EMAIL": "<<EMAIL>>"}
        analyzer_results = [RecognizerResult("EMAIL", 12, 28, 0.8)]
        masked_message = mask_message(message, redact_policies_dict, analyzer_results)
        self.assertEqual(masked_message, "My email is <<EMAIL>>")

    def test_merge_scanner_results_with_multiple_results(self):
        scanner_results = [
            ScannerResult(traits=["PII"], analyzer_result=[{"entity_type": "EMAIL"}]),
            ScannerResult(traits=["TOXIC"], analyzer_result=[{"entity_type": "TOXIC"}])
        ]
        merged_result = merge_scanner_results(scanner_results)
        self.assertEqual(merged_result.traits, ["PII", "TOXIC"])
        self.assertEqual(merged_result.analyzer_result, [{"entity_type": "EMAIL"}, {"entity_type": "TOXIC"}])

    @patch('api.shield.services.guardrail_service.PIIScanner.scan')
    @patch('api.shield.services.guardrail_service.ToxicContentScanner.scan')
    def test_test_paig_guardrail_with_sensitive_data(self, mock_toxic_scan, mock_pii_scan):
        transformed_response = {
            "config_type": {
                "SENSITIVE_DATA": {
                    "configs": {"PII": "DENY"},
                    "response_message": "Sensitive data found"
                }
            }
        }
        message = "My email is test@example.com"
        mock_pii_scan.return_value = ScannerResult(traits=["PII"], analyzer_result=[{"entity_type": "EMAIL"}])
        mock_toxic_scan.return_value = ScannerResult(traits=[], analyzer_result=[])
        result = paig_guardrail_test(transformed_response, message)
        self.assertEqual(result, {"action": "DENY", "tags": ["PII"], "policy": ["SENSITIVE_DATA"], "message": "Sensitive data found"})



@pytest.mark.asyncio
async def test_test_guardrail():
    mock_aws_scanner = MagicMock()
    mock_aws_scanner.scan.return_value = ScannerResult(actions=["DENY"], traits=["HARMFUL"])

    mock_pii_scanner = MagicMock()
    mock_pii_scanner.scan.return_value = ScannerResult(traits=[])
    # Mock the async function decrypted_connection_details
    with patch("api.shield.services.guardrail_service.decrypted_connection_details", new_callable=AsyncMock) as mock_decrypt, \
            patch("api.shield.services.guardrail_service.AWSBedrockGuardrailScanner", return_value=mock_aws_scanner), \
            patch("api.shield.services.guardrail_service.PIIScanner", return_value=mock_pii_scanner):

        # Mock decrypted_connection_details to do nothing
        mock_decrypt.return_value = None

        transformed_response = {
            "guardrail_provider_details": {
                "AWS": {
                    "guardrailId": "123",
                    "version": "1.0",
                    "connection_details": {"region": "us-west-2"}
                }
            },
            "config_type": {
                "policy1": {
                    "configs": {"HARMFUL": "DENY"},
                    "response_message": "Policy violation detected!"
                }
            }
        }

        result = await do_test_guardrail("tenant-123", transformed_response, "test message")

        assert result == [{
            "action": "DENY",
            "tags": ["HARMFUL"],
            "policies": ["policy1"],
            "message": "Policy violation detected!"
        }]

        # Ensure the async function was awaited
        mock_decrypt.assert_awaited_once_with("tenant-123", {"region": "us-west-2"})

@pytest.mark.asyncio
async def test_aws_guardrail_test_with_no_aws_guardrail():
    transformed_response = {
        "guardrail_provider_details": {
            "OLLAMA": {
                "guardrailId": "123",
                "version": "1.0",
                "connection_details": {"region": "us-west-2"}
            }
        },
        "config_type": {
            "policy1": {
                "configs": {"HARMFUL": "DENY"},
                "response_message": "Policy violation detected!"
            }
        }
    }

    result = await aws_guardrail_test("tenant-123", transformed_response, "test message")

    assert result == {}

@pytest.mark.asyncio
async def test_aws_guardrail_test_with_aws_guardrail():
    mock_aws_scanner = MagicMock()
    mock_aws_scanner.scan.return_value = ScannerResult(actions=["DENY"], traits=["HARMFUL"])

    # Mock the async function decrypted_connection_details
    with patch("api.shield.services.guardrail_service.decrypted_connection_details", new_callable=AsyncMock) as mock_decrypt, \
            patch("api.shield.services.guardrail_service.AWSBedrockGuardrailScanner", return_value=mock_aws_scanner):

        # Mock decrypted_connection_details to do nothing
        mock_decrypt.return_value = None

        transformed_response = {
            "guardrail_provider_details": {
                "AWS": {
                    "guardrailId": "123",
                    "version": "1.0",
                    "connection_details": {"region": "us-west-2"}
                }
            },
            "config_type": {
                "policy1": {
                    "configs": {"HARMFUL": "DENY"},
                    "response_message": "Policy violation detected!"
                }
            }
        }

        result = await aws_guardrail_test("tenant-123", transformed_response, "test message")

        assert result == {
            "action": "DENY",
            "tags": ["HARMFUL"],
            "policy": ["policy1"],
            "message": "Policy violation detected!"
        }

        # Ensure the async function was awaited
        mock_decrypt.assert_awaited_once_with("tenant-123", {"region": "us-west-2"})

class TestMergeFinalResult(unittest.TestCase):

    def test_merge_final_result_with_deny_priority(self):
        """Test that DENY action takes priority over ALLOW and REDACT"""
        from api.shield.services.guardrail_service import merge_final_result
        
        final_result = [
            {"action": "ALLOW", "tags": ["TAG1"], "policy": ["POLICY1"], "message": "Allow message"},
            {"action": "DENY", "tags": ["TAG2"], "policy": ["POLICY2"], "message": "Deny message"},
            {"action": "REDACT", "tags": ["TAG3"], "policy": ["POLICY3"], "message": "Redact message"}
        ]
        
        result = merge_final_result(final_result)
        
        expected = {
            "action": "DENY",
            "tags": ["TAG1", "TAG2", "TAG3"],
            "policies": ["POLICY1", "POLICY2", "POLICY3"],
            "message": "Deny message"
        }
        self.assertEqual(result, expected)

    def test_merge_final_result_with_redact_priority(self):
        """Test that REDACT action takes priority over ALLOW"""
        from api.shield.services.guardrail_service import merge_final_result
        
        final_result = [
            {"action": "ALLOW", "tags": ["TAG1"], "policy": ["POLICY1"], "message": "Allow message"},
            {"action": "REDACT", "tags": ["TAG2"], "policy": ["POLICY2"], "message": "Redact message"}
        ]
        
        result = merge_final_result(final_result)
        
        expected = {
            "action": "REDACT",
            "tags": ["TAG1", "TAG2"],
            "policies": ["POLICY1", "POLICY2"],
            "message": "Redact message"
        }
        self.assertEqual(result, expected)

    def test_merge_final_result_with_all_allow(self):
        """Test merge when all actions are ALLOW"""
        from api.shield.services.guardrail_service import merge_final_result
        
        final_result = [
            {"action": "ALLOW", "tags": ["TAG1"], "policy": ["POLICY1"], "message": "Allow message 1"},
            {"action": "ALLOW", "tags": ["TAG2"], "policy": ["POLICY2"], "message": "Allow message 2"}
        ]
        
        result = merge_final_result(final_result)
        
        expected = {
            "action": "ALLOW",
            "tags": ["TAG1", "TAG2"],
            "policies": ["POLICY1", "POLICY2"],
            "message": "Allow message 1"  # First message is kept for same priority
        }
        self.assertEqual(result, expected)

    def test_merge_final_result_with_empty_list(self):
        """Test merge with empty result list"""
        from api.shield.services.guardrail_service import merge_final_result
        
        final_result = []
        
        result = merge_final_result(final_result)
        
        expected = {
            "action": "ALLOW",
            "tags": [],
            "policies": [],
            "message": ""
        }
        self.assertEqual(result, expected)

    def test_merge_final_result_with_missing_fields(self):
        """Test merge when some fields are missing in results"""
        from api.shield.services.guardrail_service import merge_final_result
        
        final_result = [
            {"action": "DENY", "message": "Deny message"},  # Missing tags and policy
            {"tags": ["TAG1"], "policy": ["POLICY1"]},  # Missing action and message
        ]
        
        result = merge_final_result(final_result)
        
        expected = {
            "action": "DENY",
            "tags": ["TAG1"],
            "policies": ["POLICY1"],
            "message": "Deny message"
        }
        self.assertEqual(result, expected)

    def test_merge_final_result_with_multiple_same_priority(self):
        """Test that first message is kept when actions have same priority"""
        from api.shield.services.guardrail_service import merge_final_result
        
        final_result = [
            {"action": "DENY", "tags": ["TAG1"], "policy": ["POLICY1"], "message": "First deny"},
            {"action": "DENY", "tags": ["TAG2"], "policy": ["POLICY2"], "message": "Second deny"}
        ]
        
        result = merge_final_result(final_result)
        
        expected = {
            "action": "DENY",
            "tags": ["TAG1", "TAG2"],
            "policies": ["POLICY1", "POLICY2"],
            "message": "First deny"  # First message is kept
        }
        self.assertEqual(result, expected)

    async def test_do_test_guardrail_with_multiple_results(self):
        # Mock PAIG guardrail test
        mocker.patch(
            'api.shield.services.guardrail_service.paig_guardrail_test',
            return_value={
                "action": "REDACT",
                "tags": ["SSN"],
                "policy": ["SENSITIVE_DATA"],
                "message": "Masked message"
            }
        )

        # Mock AWS guardrail test
        mocker.patch(
            'api.shield.services.guardrail_service.aws_guardrail_test',
            return_value={
                "action": "DENY",
                "tags": ["TOXIC"],
                "policy": ["TOXIC_CONTENT"],
                "message": "Toxic content detected"
            }
        )

        transformed_response = {
            "config_type": {
                "SENSITIVE_DATA": {
                    "configs": {"SSN": "REDACT"}
                },
                "TOXIC_CONTENT": {
                    "configs": {"TOXIC": "DENY"}
                }
            }
        }

        result = await do_test_guardrail("test-tenant", transformed_response, "Test message")
        assert len(result) == 1
        assert result[0]["action"] == "DENY"  # DENY takes precedence over REDACT
        assert sorted(result[0]["tags"]) == ["SSN", "TOXIC"]
        assert sorted(result[0]["policies"]) == ["SENSITIVE_DATA", "TOXIC_CONTENT"]
        assert result[0]["message"] == "Toxic content detected"