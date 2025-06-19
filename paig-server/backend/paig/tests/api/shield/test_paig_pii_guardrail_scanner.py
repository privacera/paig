from api.shield.model.scanner_result import ScannerResult
from api.shield.scanners.PAIGPIIGuardrailScanner import PAIGPIIGuardrailScanner

class TestPAIGPIIGuardrailScanner:

    # Scanner returns ScannerResult with empty traits when no policies are triggered
    def test_scanner_returns_empty_traits_when_no_policies_triggered(self, mocker):
        # Arrange
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=([], {}, []))
        scanner = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS"],
            sensitive_data_config={"configs": {}}
        )

        # Act
        result = scanner.scan("Test message")

        # Assert
        assert isinstance(result, ScannerResult)
        assert result.get_traits() == []
        assert result.get("actions", None) is None

    # Scanner returns ScannerResult with BLOCKED action when deny policies are found
    def test_scanner_returns_blocked_action_when_deny_policies_found(self, mocker):
        # Arrange
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=(["EMAIL_ADDRESS"], {}, []))
        scanner = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS"],
            sensitive_data_config={"configs": {"EMAIL_ADDRESS": "DENY"}, "response_message": "PII detected"}
        )

        # Act
        result = scanner.scan("Test message with email@example.com")

        # Assert
        assert isinstance(result, ScannerResult)
        assert result.get_traits() == []
        assert result.get("actions") == ["BLOCKED"]
        assert result.get("output_text") == "PII detected"

    # Scanner returns ScannerResult with REDACT action when redact policies are found
    def test_scanner_returns_redact_action_when_redact_policies_found(self, mocker):
        # Arrange
        redact_policies = {"EMAIL_ADDRESS": "<<EMAIL_ADDRESS>>"}
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=([], redact_policies, []))
        scanner = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS"],
            sensitive_data_config={"configs": {"EMAIL_ADDRESS": "REDACT"}}
        )

        # Act
        result = scanner.scan("Test message with email@example.com")

        # Assert
        assert isinstance(result, ScannerResult)
        assert result.get_traits() == []
        assert result.get("actions") == ["ANONYMIZED"]
        assert result.get("masked_traits") == redact_policies

    # Handle case when pii_traits is None or empty
    def test_scanner_handles_none_or_empty_pii_traits(self, mocker):
        # Arrange
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=([], {}, []))

        # Test with None pii_traits
        scanner_none = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=None,
            sensitive_data_config={"configs": {}}
        )

        # Test with empty pii_traits
        scanner_empty = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=[],
            sensitive_data_config={"configs": {}}
        )

        # Act
        result_none = scanner_none.scan("Test message")
        result_empty = scanner_empty.scan("Test message")

        # Assert
        assert isinstance(result_none, ScannerResult)
        assert result_none.get_traits() == []

        assert isinstance(result_empty, ScannerResult)
        assert result_empty.get_traits() == []

    # Handle case when sensitive_data_config is None or empty
    def test_scanner_handles_none_or_empty_sensitive_data_config(self, mocker):
        # Arrange
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=([], {}, []))

        # Test with None sensitive_data_config
        scanner_none = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS"],
            sensitive_data_config=None
        )

        # Test with empty sensitive_data_config
        scanner_empty = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS"],
            sensitive_data_config={}
        )

        # Act
        result_none = scanner_none.scan("Test message")
        result_empty = scanner_empty.scan("Test message")

        # Assert
        assert isinstance(result_none, ScannerResult)
        assert result_none.get_traits() == []

        assert isinstance(result_empty, ScannerResult)
        assert result_empty.get_traits() == []

    # Handle case when response_message is missing in sensitive_data_config
    def test_scanner_handles_missing_response_message(self, mocker):
        # Arrange
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=(["EMAIL_ADDRESS"], {}, []))
        scanner = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS"],
            sensitive_data_config={"configs": {"EMAIL_ADDRESS": "DENY"}}  # No response_message
        )

        # Act
        result = scanner.scan("Test message with email@example.com")

        # Assert
        assert isinstance(result, ScannerResult)
        assert result.get_traits() == []
        assert result.get("actions") == ["BLOCKED"]
        assert result.get("output_text") == None  # Should handle None response_message

    # Handle case when both deny_policies_list and redact_policies_dict have values
    def test_scanner_prioritizes_deny_over_redact_when_both_present(self, mocker):
        # Arrange
        deny_policies = ["EMAIL_ADDRESS"]
        redact_policies = {"PHONE_NUMBER": "<<PHONE_NUMBER>>"}
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=(deny_policies, redact_policies, []))
        scanner = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS", "PHONE_NUMBER"],
            sensitive_data_config={
                "configs": {
                    "EMAIL_ADDRESS": "DENY",
                    "PHONE_NUMBER": "REDACT"
                },
                "response_message": "PII detected"
            }
        )

        # Act
        result = scanner.scan("Test message with email@example.com and 123-456-7890")

        # Assert
        assert isinstance(result, ScannerResult)
        assert result.get_traits() == []
        assert result.get("actions") == ["BLOCKED"]
        assert result.get("output_text") == "PII detected"
        # Should not have masked_traits since DENY takes precedence
        assert result.get("masked_traits", None) is None

    # Scanner returns ScannerResult with ALLOWED action when allow policies are found
    def test_scanner_returns_allowed_action_when_allow_policies_found(self, mocker):
        # Arrange
        mocker.patch('api.shield.services.guardrail_service.paig_pii_guardrail_evaluation',
                     return_value=([], {}, ["EMAIL_ADDRESS"]))
        scanner = PAIGPIIGuardrailScanner(
            name="TestScanner",
            pii_traits=["EMAIL_ADDRESS"],
            sensitive_data_config={"configs": {"EMAIL_ADDRESS": "ALLOW"}}
        )

        # Act
        result = scanner.scan("Test message with email@example.com")

        # Assert
        assert isinstance(result, ScannerResult)
        assert result.get_traits() == []
        assert result.get("actions") == ["ALLOWED"]
        assert result.get("masked_traits", None) is None
        assert result.get("output_text", None) == "Test message with email@example.com"