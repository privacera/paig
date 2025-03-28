import pytest

from services.langchain_service_intf import LangChainServiceIntf


@pytest.mark.parametrize("input_message, expected_output", [
    ("ERROR: PAIG-123456: Some error occurred", "Some error occurred"),
    ("ERROR: PAIG-987654: Another error happened", "Another error happened"),
    ("Some message without error code", "Some message without error code"),
    ("ERROR: PAIG-111111: ERROR: PAIG-222222: Chained errors", "Chained errors"),
    ("ERROR:    PAIG-333333:   Extra spaces handled", "Extra spaces handled"),
    ("", ""),
])
def test_remove_error_code(input_message, expected_output):
    assert LangChainServiceIntf.remove_error_code(input_message) == expected_output