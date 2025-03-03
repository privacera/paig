from api.guardrails.providers.exceptions import GuardrailException


# Unit tests for GuardrailException
def test_guardrail_exception_with_details():
    """Test that GuardrailException correctly initializes with a message and details."""
    message = "Test guardrail error"
    details = {"error_code": 123, "info": "Additional error context"}

    exception = GuardrailException(message, details)

    assert str(exception) == message  # Check that the message is correctly passed to the exception
    assert exception.details == details  # Check that the details are correctly passed


def test_guardrail_exception_without_details():
    """Test that GuardrailException initializes with default empty details when no details are provided."""
    message = "Test guardrail error"

    exception = GuardrailException(message)

    assert str(exception) == message  # Check that the message is correctly passed to the exception
    assert exception.details == {}  # Check that details default to an empty dictionary


def test_guardrail_exception_details_mutability():
    """Test that modifying the details attribute of the exception works correctly."""
    message = "Test guardrail error"
    details = {"error_code": 123}

    exception = GuardrailException(message, details)

    # Modify the details attribute after initialization
    exception.details["info"] = "Updated error context"

    assert exception.details["info"] == "Updated error context"  # Ensure the attribute is mutable
