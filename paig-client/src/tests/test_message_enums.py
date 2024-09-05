import paig_client.message
import pytest

def test_enum():
    info_msg = paig_client.message.InfoMessage.PAIG_IS_INITIALIZED.format(kwargs={"a": "b"})
    print(info_msg)

    error_msg = paig_client.message.ErrorMessage.PAIG_IS_ALREADY_INITIALIZED.format()
    print(error_msg)

    warning_msg = paig_client.message.WarningMessage.APP_CONFIG_FILE_NOT_FOUND_IN_PARAMETER.format(
        file_path="./paig_conf")
    print(warning_msg)

    print(paig_client.message.ErrorMessage.SHIELD_SERVER_INITIALIZATION_FAILED.format(response_status="status",
                                                                                           response_data="body"))

def test_enum_duplicate():

    with pytest.raises(ValueError):
        @paig_client.message.unique_message_enum
        class TestEnumWithDuplicates(paig_client.message.BaseMessage):
            A = 1, "a"
            B = 1, "b"

        test_enum = TestEnumWithDuplicates.B

def test_enum_without_duplicates():
    @paig_client.message.unique_message_enum
    class TestEnumWithoutDuplicates(paig_client.message.BaseMessage):
        A = 1, "a"
        B = 2, "b"

    test_enum = TestEnumWithoutDuplicates.B