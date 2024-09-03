import pytest
from src.privacera_shield_common.paig_exception import PAIGException


def test_paig_exception():
    message = "Test exception message"
    exception = PAIGException(message)
    assert str(exception) == message
    assert exception.message == message
