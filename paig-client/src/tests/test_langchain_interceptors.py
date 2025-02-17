import logging
import pytest
from langchain.schema import LLMResult, Generation

import paig_client.interceptor_setup
import paig_client.client
import paig_client.core
import paig_client.langchain_callback
import paig_client.interceptor
import paig_client.langchain_method_interceptor
from paig_client.backend import ShieldAccessResult
from unittest.mock import patch

SHIELD_SERVER_URL = "http://localhost:8000"

_logger = logging.getLogger(__name__)


@pytest.mark.interceptor_test
def test_langchain_llm_get_all_methods_to_intercept(setup_paig_plugin_with_app_config_file_name):
    langchain_llm_setup = paig_client.langchain_method_interceptor.LangChainMethodInterceptor()
    langchain_llm_setup.find_all_methods_to_intercept()
    # Verify that the number of intercepted methods matches the expected count.
    # Note: This value may change if the LangChain dependency is updated
    assert len(langchain_llm_setup.list_of_methods_to_intercept) == 122
    langchain_llm_setup.undo_setup_interceptors()


#    or len(
# langchain_llm_setup.list_of_methods_to_intercept) == 85  # TODO sometimes it is 85


@pytest.mark.interceptor_test
def test_langchain_get_baseopenai_methods_to_intercept(setup_paig_plugin_with_app_config_file_name):
    langchain_llm_setup = paig_client.langchain_method_interceptor.LangChainMethodInterceptor(
        filter_in_classes=["BaseOpenAI"])
    langchain_llm_setup.find_all_methods_to_intercept()
    assert len(langchain_llm_setup.list_of_methods_to_intercept) == 4
    #    or len(
    # langchain_llm_setup.list_of_methods_to_intercept) == 2  # TODO sometimes it is 2
    langchain_llm_setup.undo_setup_interceptors()


@pytest.mark.e2e_test
def test_b_langchain_set_baseopenai_interceptor(setup_paig_plugin_with_app_config_file_name):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        with patch("paig_client.backend.ShieldRestHttpClient.is_access_allowed",
                   return_value=ShieldAccessResult(
                       **{"isAllowed": True, "responseMessages": [{"responseText": "hello world"}]})):
            paig_client.client.setup(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                          frameworks=["langchain"])

            # langchain_llm_setup = paig_client.langchain_callback.LangChainMethodInterceptor(
            #     filter_in_classes=["FakeListLLM"])
            # langchain_llm_setup.find_all_methods_to_intercept()
            # langchain_llm_setup.setup_interceptors(paig_client.core._paig_plugin)
            #
            # assert len(langchain_llm_setup.list_of_methods_to_intercept) == 1

            paig_client.client.set_current_user("user1")
            from langchain.llms.fake import FakeListLLM
            llm = FakeListLLM(responses=["response number 1", "response number 2", "response number 3"])
            for i in range(10):
                _logger.debug("will invoke llm(prompt)")
                _logger.debug(llm.invoke(f"prompt number {i}"))
                _logger.debug(llm.generate(prompts=[f"prompt number {i}"]))
            paig_client.client.clear()


def test_BaseLLMGenerateCallback(setup_paig_plugin_with_app_config_file_name):
    with patch("paig_client.backend.ShieldRestHttpClient.init_shield_server", return_value=None):
        with patch("paig_client.backend.ShieldRestHttpClient.is_access_allowed",
                   return_value=ShieldAccessResult(
                       **{"isAllowed": True, "responseMessages": [{"responseText": "hello world"}]})):
            paig_client.client.setup(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                          frameworks=["None"])

            class TestClass:
                def __init__(self, responses):
                    self.responses = responses

                def generate(self, prompts):
                    generations = [[Generation(text=response)] for response in self.responses]
                    return LLMResult(generations=generations)

            paig_client.interceptor.wrap_method(paig_client.core._paig_plugin, TestClass, "generate",
                                                     TestClass.generate,
                                                     paig_client.langchain_method_interceptor.BaseLLMGenerateCallback)
            test_class = TestClass(["response number 1", "response number 2", "response number 3"])
            test_class.generate(["prompt number 1", "prompt number 2", "prompt number 3"])
