import privacera_shield.message
import pytest

def test_enum():
    info_msg = privacera_shield.message.InfoMessage.PAIG_IS_INITIALIZED.format(kwargs={"a": "b"})
    print(info_msg)

    error_msg = privacera_shield.message.ErrorMessage.PAIG_IS_ALREADY_INITIALIZED.format()
    print(error_msg)

    warning_msg = privacera_shield.message.WarningMessage.APP_CONFIG_FILE_NOT_FOUND_IN_PARAMETER.format(
        file_path="./paig_conf")
    print(warning_msg)

    print(privacera_shield.message.ErrorMessage.SHIELD_SERVER_INITIALIZATION_FAILED.format(response_status="status",
                                                                                           response_data="body"))

def test_enum_duplicate():

    with pytest.raises(ValueError):
        @privacera_shield.message.unique_message_enum
        class TestEnumWithDuplicates(privacera_shield.message.BaseMessage):
            A = 1, "a"
            B = 1, "b"

        test_enum = TestEnumWithDuplicates.B

def test_enum_without_duplicates():
    @privacera_shield.message.unique_message_enum
    class TestEnumWithoutDuplicates(privacera_shield.message.BaseMessage):
        A = 1, "a"
        B = 2, "b"

    test_enum = TestEnumWithoutDuplicates.B