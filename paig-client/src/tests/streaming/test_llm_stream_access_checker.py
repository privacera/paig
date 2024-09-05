import logging
from unittest.mock import Mock, patch
import pytest

from paig_client.backend import StreamAccessAuditRequest
from paig_client.core import LLMStreamAccessChecker, ConversationType, PAIGPlugin
from paig_client.exception import AccessControlException, PAIGException
from paig_client.message import ErrorMessage

# Mock the logger
_logger = logging.getLogger(__name__)

def test_check_access_for_sentence():
    """
    Test function to check the check_access_for_sentence method of the LLMStreamAccessChecker class.
    """
    mock_paig_plugin = Mock()
    mock_paig_application = Mock()
    mock_access_result = Mock()
    mock_access_result.get_response_messages.return_value = [Mock(get_response_text=Mock(return_value="Sample sentence."))]
    mock_paig_application.authorize.return_value = mock_access_result
    mock_paig_plugin.get_current_application.return_value = mock_paig_application

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    response = llm_stream_access_checker.check_access_for_sentence("Sample sentence.")

    assert response == "Sample sentence."
    mock_paig_application.authorize.assert_called_once_with(
        text="Sample sentence.",
        conversation_type=ConversationType.REPLY,
        thread_id=mock_paig_plugin.get_current("thread_id"),
        stream_id=llm_stream_access_checker.stream_id,
        enable_audit=False
    )


def test_check_access_for_sentence_allowed_false():
    """
    Test function to check the check_access_for_sentence method of the LLMStreamAccessChecker class.
    """
    mock_paig_plugin = Mock()
    mock_paig_application = Mock()
    mock_access_result = Mock(get_is_allowed=Mock(return_value=False))
    mock_access_result.get_response_messages.return_value = [Mock(get_response_text=Mock(return_value="Sample sentence."))]
    mock_paig_application.authorize.return_value = mock_access_result
    mock_paig_plugin.get_current_application.return_value = mock_paig_application

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    with pytest.raises(AccessControlException):
        llm_stream_access_checker.check_access_for_sentence("Sample sentence.")


def test_check_access_with_complete_sentence():
    """
    Test function to check the check_access method with an incomplete sentence input.
    """
    mock_paig_plugin = Mock()
    mock_paig_application = Mock()
    mock_access_result = Mock()
    mock_access_result.get_response_messages.return_value = [Mock(get_response_text=Mock(return_value="Complete sentence."))]
    mock_paig_application.authorize.return_value = mock_access_result
    mock_paig_plugin.get_current_application.return_value = mock_paig_application

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    response = llm_stream_access_checker.check_access("Complete sentence.")

    assert response == "Complete sentence."
    assert llm_stream_access_checker.llm_reply_text == ""


def test_check_access_with_incomplete_sentence():
    """
    Test function to check the check_access method with an incomplete sentence input.
    """
    mock_paig_plugin = Mock()
    mock_paig_application = Mock()
    mock_access_result = Mock()
    mock_access_result.get_response_messages.return_value = [Mock(get_response_text=Mock(return_value="Incomplete sentence. "))]
    mock_paig_application.authorize.return_value = mock_access_result
    mock_paig_plugin.get_current_application.return_value = mock_paig_application

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    response = llm_stream_access_checker.check_access("Incomplete sentence. I am ")

    assert response == "Incomplete sentence. "
    assert llm_stream_access_checker.llm_reply_text == "I am "

    incomplete_response = llm_stream_access_checker.check_access_for_incomplete_sentence()
    assert llm_stream_access_checker.llm_reply_text == ""


def test_check_access_with_multiple_sentences():
    """
    Test function to check the check_access method with multiple sentences as input.
    """
    mock_paig_plugin = Mock()
    mock_paig_application = Mock()
    mock_access_result = Mock()
    mock_access_result.get_response_messages.return_value = [Mock(get_response_text=Mock(return_value="First sentence. "))]
    mock_paig_application.authorize.return_value = mock_access_result
    mock_paig_plugin.get_current_application.return_value = mock_paig_application

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    response = llm_stream_access_checker.check_access("First ")
    assert response == ""
    assert llm_stream_access_checker.llm_reply_text == "First "

    response = llm_stream_access_checker.check_access("sentence. ")
    assert response == "First sentence. "
    assert llm_stream_access_checker.llm_reply_text == ""

    response = llm_stream_access_checker.check_access("Second ")
    assert response == ""
    assert llm_stream_access_checker.llm_reply_text == "Second "


def test_get_llm_stream_access_checker_none():
    """
    Test function to check the get_llm_stream_access_checker method when no instance of LLMStreamAccessChecker exists.
    """
    paig_plugin = PAIGPlugin(frameworks=[])
    with pytest.raises(RuntimeError):
        paig_plugin.get_llm_stream_access_checker()


def test_create_llm_stream_access_checker():
    """
    Test function to check the create_llm_stream_access_checker method of the PAIGPlugin class.
    """
    paig_plugin = PAIGPlugin(frameworks=[])
    paig_plugin.create_llm_stream_access_checker()
    assert paig_plugin.get_llm_stream_access_checker() is not None


def test_cleanup_llm_stream_access_checker():
    """
    Test function to check the cleanup_llm_stream_access_checker method of the PAIGPlugin class.
    """
    paig_plugin = PAIGPlugin(frameworks=[])
    paig_plugin.create_llm_stream_access_checker()
    assert paig_plugin.get_llm_stream_access_checker() is not None
    paig_plugin.cleanup_llm_stream_access_checker()
    with pytest.raises(RuntimeError):
        paig_plugin.get_llm_stream_access_checker()


def test_create_stream_access_audit_request_masked():
    mock_paig_plugin = Mock()

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    # Mocking dependencies and data
    llm_stream_access_checker.shield_access_response_list = [
        Mock(isAllowed=True, responseMessages=[
            {"traits": ["trait1"], "maskedTraits": {"trait2": "masked_trait"}, "analyzerResult": ["result1"],
             "rangerAuditIds": ["ranger_audit_id1"], "rangerPolicyIds": ["ranger_policy_id1"],
             "paigPolicyIds": ["paig_policy_id1"], "applicationName": "TestApp"},
            {"traits": ["trait3"], "maskedTraits": {"trait4": "masked_trait"}, "analyzerResult": ["result2"],
             "rangerAuditIds": ["ranger_audit_id2"], "rangerPolicyIds": ["ranger_policy_id2"],
             "paigPolicyIds": ["paig_policy_id2"], "applicationName": "TestApp"}
        ]),
        Mock(isAllowed=True, responseMessages=[
            {"traits": ["trait5"], "maskedTraits": {"trait6": "masked_trait"}, "analyzerResult": ["result3"],
             "rangerAuditIds": ["ranger_audit_id3"], "rangerPolicyIds": ["ranger_policy_id3"],
             "paigPolicyIds": ["paig_policy_id3"], "applicationName": "TestApp"}
        ])
    ]

    llm_stream_access_checker.llm_original_full_reply = "original_full_reply"
    llm_stream_access_checker.llm_masked_full_reply = "masked_full_reply"

    llm_stream_access_checker.paig_plugin.get_current_application.return_value.tenant_id = "tenant_id"
    llm_stream_access_checker.paig_plugin.get_client_application_key.return_value = "client_application_key"
    llm_stream_access_checker.paig_plugin.get_application_key.return_value = "application_key"

    mock_paig_plugin.get_current.return_value = "current_user"

    request = llm_stream_access_checker.create_stream_access_audit_request()

    assert isinstance(request, StreamAccessAuditRequest)
    assert request.tenant_id == "tenant_id"
    assert request.request_id == llm_stream_access_checker.shield_access_response_list[-1].requestId
    assert request.thread_id == llm_stream_access_checker.shield_access_response_list[-1].threadId
    assert request.thread_sequence_number == llm_stream_access_checker.shield_access_response_list[-1].sequenceNumber
    assert request.request_type == ConversationType.REPLY
    assert request.user_id == "current_user"
    assert request.client_application_key == "client_application_key"
    assert request.application_key == "application_key"
    assert request.application_name == llm_stream_access_checker.shield_access_response_list[-1].responseMessages[0]["applicationName"]
    assert request.result == "masked"  # Since there is at least one denied response
    assert request.traits == ["trait1", "trait3", "trait5"]
    assert request.masked_traits == {"trait2": "masked_trait", "trait4": "masked_trait", "trait6": "masked_trait"}
    assert request.messages == [{
        "originalMessage": "original_full_reply",
        "maskedMessage": "masked_full_reply",
        "analyzerResult": '["result1", "result2", "result3"]'
    }]
    assert request.ranger_audit_ids == ["ranger_audit_id1", "ranger_audit_id2", "ranger_audit_id3"]
    assert request.ranger_policy_ids == ["ranger_policy_id1", "ranger_policy_id2", "ranger_policy_id3"]
    assert request.paig_policy_ids == ["paig_policy_id1", "paig_policy_id2", "paig_policy_id3"]
    assert request.client_ip is not None or request.client_ip != ""
    assert request.client_hostname is not None or request.client_hostname != ""


def test_create_stream_access_audit_request_denied():
    mock_paig_plugin = Mock()

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    # Mocking dependencies and data
    llm_stream_access_checker.shield_access_response_list = [
        Mock(isAllowed=True, responseMessages=[
            {"traits": ["trait1"], "maskedTraits": {"trait2": "masked_trait"}, "analyzerResult": ["result1"],
             "rangerAuditIds": ["ranger_audit_id1"], "rangerPolicyIds": ["ranger_policy_id1"],
             "paigPolicyIds": ["paig_policy_id1"], "applicationName": "TestApp"},
            {"traits": ["trait3"], "maskedTraits": {"trait4": "masked_trait"}, "analyzerResult": ["result2"],
             "rangerAuditIds": ["ranger_audit_id2"], "rangerPolicyIds": ["ranger_policy_id2"],
             "paigPolicyIds": ["paig_policy_id2"], "applicationName": "TestApp"}
        ]),
        Mock(isAllowed=False, responseMessages=[
            {"traits": ["trait5"], "maskedTraits": {"trait6": "masked_trait"}, "analyzerResult": ["result3"],
             "rangerAuditIds": ["ranger_audit_id3"], "rangerPolicyIds": ["ranger_policy_id3"],
             "paigPolicyIds": ["paig_policy_id3"], "applicationName": "TestApp"}
        ])
    ]

    llm_stream_access_checker.llm_original_full_reply = "original_full_reply"
    llm_stream_access_checker.llm_masked_full_reply = "masked_full_reply"

    llm_stream_access_checker.paig_plugin.get_current_application.return_value.tenant_id = "tenant_id"
    llm_stream_access_checker.paig_plugin.get_client_application_key.return_value = "client_application_key"
    llm_stream_access_checker.paig_plugin.get_application_key.return_value = "application_key"

    mock_paig_plugin.get_current.return_value = "current_user"

    request = llm_stream_access_checker.create_stream_access_audit_request()

    assert isinstance(request, StreamAccessAuditRequest)
    assert request.tenant_id == "tenant_id"
    assert request.request_id == llm_stream_access_checker.shield_access_response_list[-1].requestId
    assert request.thread_id == llm_stream_access_checker.shield_access_response_list[-1].threadId
    assert request.thread_sequence_number == llm_stream_access_checker.shield_access_response_list[-1].sequenceNumber
    assert request.request_type == ConversationType.REPLY
    assert request.user_id == "current_user"
    assert request.client_application_key == "client_application_key"
    assert request.application_key == "application_key"
    assert request.application_name == llm_stream_access_checker.shield_access_response_list[-1].responseMessages[0]["applicationName"]
    assert request.result == "denied"  # Since there is at least one denied response
    assert request.traits == ["trait1", "trait3", "trait5"]
    assert request.masked_traits == {"trait2": "masked_trait", "trait4": "masked_trait", "trait6": "masked_trait"}
    assert request.messages == [{
        "originalMessage": "original_full_reply",
        "maskedMessage": "masked_full_reply",
        "analyzerResult": '["result1", "result2", "result3"]'
    }]
    assert request.ranger_audit_ids == ["ranger_audit_id1", "ranger_audit_id2", "ranger_audit_id3"]
    assert request.ranger_policy_ids == ["ranger_policy_id1", "ranger_policy_id2", "ranger_policy_id3"]
    assert request.paig_policy_ids == ["paig_policy_id1", "paig_policy_id2", "paig_policy_id3"]
    assert request.client_ip is not None or request.client_ip != ""
    assert request.client_hostname is not None or request.client_hostname != ""

def test_flush_audits_with_logs():
    # Mocking dependencies
    mock_paig_plugin = Mock()

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    llm_stream_access_checker.shield_access_response_list = [Mock()]

    # Mocking create_stream_access_audit_request method
    llm_stream_access_checker.create_stream_access_audit_request = Mock(return_value=Mock())

    # Mocking shield_client
    mock_shield_client = Mock()
    llm_stream_access_checker.paig_plugin.get_current_application.return_value.shield_client = mock_shield_client

    # Execute the method
    llm_stream_access_checker.flush_audits()

    # Assertions
    llm_stream_access_checker.create_stream_access_audit_request.assert_called_once()
    mock_paig_plugin.log_stream_access_audit.assert_called_once_with(
        llm_stream_access_checker.create_stream_access_audit_request.return_value)

def test_flush_audits_without_logs():
    # Mocking dependencies
    mock_paig_plugin = Mock()

    llm_stream_access_checker = LLMStreamAccessChecker(mock_paig_plugin)

    llm_stream_access_checker.shield_access_response_list = []

    # Mocking _logger
    mock_logger = Mock()
    llm_stream_access_checker._logger = mock_logger

    # Execute the method
    llm_stream_access_checker.flush_audits()
