
import pytest
from core.exceptions.base import BadRequestException
from api.governance.services.metadata_value_service import MetadataValueRequestValidator

validator = MetadataValueRequestValidator()

@pytest.mark.parametrize("invalid_value, expected_message", [
    (None, "Attribute 'metadataValue' is required"),
    ("", "Attribute 'metadataValue' cannot be empty or whitespace"),
    ("   ", "Attribute 'metadataValue' cannot be empty or whitespace"),
])
def test_validate_metadata_attr_value_invalid(invalid_value, expected_message):
    with pytest.raises(BadRequestException) as exc_info:
        validator.validate_metadata_attr_value(invalid_value)

    assert expected_message in str(exc_info.value)

def test_validate_metadata_attr_value_valid():
    try:
        validator.validate_metadata_attr_value("ValidValue")
    except Exception:
        pytest.fail("validate_metadata_attr_value raised an exception unexpectedly!")
