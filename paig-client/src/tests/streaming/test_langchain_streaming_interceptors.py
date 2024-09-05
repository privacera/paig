from unittest.mock import Mock

import pytest

import paig_client
from paig_client.exception import AccessControlException
from paig_client.langchain_streaming_interceptor import LangChainStreamingInterceptor, LangchainStreamingCallback


@pytest.mark.interceptor_test
def test_langchain_streaming_get_all_methods_to_intercept():
    """
    Test function to verify the behavior of the LangChainStreamingInterceptor's
    get_all_methods_to_intercept method.

    This test case ensures that the LangChainStreamingInterceptor correctly identifies
    and lists all the methods that need interception. It sets up the interceptor,
    verifies the list of intercepted methods, and then undoes the setup of interceptors.
    """
    langchain_streaming_setup = paig_client.langchain_streaming_interceptor.LangChainStreamingInterceptor()

    # Find all methods to intercept
    langchain_streaming_setup.find_all_methods_to_intercept()

    # Assert that only one method is listed for interception
    assert len(langchain_streaming_setup.list_of_methods_to_intercept) == 1

    # Setup Interceptors
    langchain_streaming_setup.setup_interceptors(None)

    # Undo the setup of interceptors
    langchain_streaming_setup.undo_setup_interceptors()


class TestLangchainStreamingCallback:
    def test_init(self):
        # Test initialization of LangchainStreamingCallback instance
        paig_plugin_mock = Mock()
        cls_mock = Mock()
        method_mock = Mock()
        callback = LangchainStreamingCallback(paig_plugin_mock, cls_mock, method_mock)
        callback.init()
        assert isinstance(callback, LangchainStreamingCallback)

    def test_check_access_allowed(self):
        # Test check_access method when access is allowed
        access_result_mock = Mock()
        access_result_mock.get_is_allowed.return_value = True
        callback = LangchainStreamingCallback(Mock(), Mock(), Mock())
        callback.check_access(access_result_mock)  # This should not raise an exception

    def test_check_access_not_allowed(self):
        # Test check_access method when access is not allowed (should raise AccessControlException)
        access_result_mock = Mock()
        access_result_mock.get_is_allowed.return_value = False
        access_result_mock.get_last_response_message.return_value.get_response_text.return_value = "Access denied"
        callback = LangchainStreamingCallback(Mock(), Mock(), Mock())
        with pytest.raises(AccessControlException):
            callback.check_access(access_result_mock)

    def test_process_inputs_first_token(self):
        # Test process_inputs method for the first token
        callback = LangchainStreamingCallback(Mock(), Mock(), Mock())
        llm_stream_access_checker_mock = Mock()
        llm_stream_access_checker_mock.check_access.return_value = ""
        llm_stream_access_checker_mock.is_first_reply_token_received = False
        callback.paig_plugin.get_llm_stream_access_checker.return_value = llm_stream_access_checker_mock

        args = ("Nancy",)
        chunk_mock = Mock(text="Nancy")
        kwargs = {"chunk": chunk_mock}
        updated_args, updated_kwargs = callback.process_inputs(*args, **kwargs)

        assert updated_args[0] == ""
        assert updated_kwargs["chunk"].text == ""
        assert chunk_mock.text == "Nancy"

    def test_process_inputs_subsequent_tokens(self):
        # Test process_inputs method for subsequent tokens
        callback = LangchainStreamingCallback(Mock(), Mock(), Mock())
        llm_stream_access_checker_mock = Mock()
        llm_stream_access_checker_mock.check_access.return_value = ""
        llm_stream_access_checker_mock.is_first_reply_token_received = True
        callback.paig_plugin.get_llm_stream_access_checker.return_value = llm_stream_access_checker_mock

        args = ("is",)
        chunk_mock = Mock(text="is")
        kwargs = {"chunk": chunk_mock}
        updated_args, updated_kwargs = callback.process_inputs(*args, **kwargs)

        assert updated_args[0] == ""
        assert updated_kwargs["chunk"].text == ""
        assert chunk_mock.text == ""