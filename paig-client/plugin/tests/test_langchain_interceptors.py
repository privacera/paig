import logging
import pytest
from langchain.schema import LLMResult, Generation

import privacera_shield.interceptor_setup
import privacera_shield.client
import privacera_shield.core
import privacera_shield.langchain_callback
import privacera_shield.interceptor
import privacera_shield.langchain_method_interceptor

SHIELD_SERVER_URL = "http://localhost:8000"

_logger = logging.getLogger(__name__)


@pytest.mark.interceptor_test
def test_langchain_llm_get_all_methods_to_intercept(setup_paig_plugin_with_app_config_file_name):
    langchain_llm_setup = privacera_shield.langchain_method_interceptor.LangChainMethodInterceptor()
    langchain_llm_setup.find_all_methods_to_intercept()
    assert len(langchain_llm_setup.list_of_methods_to_intercept) == 120
    langchain_llm_setup.undo_setup_interceptors()


#    or len(
# langchain_llm_setup.list_of_methods_to_intercept) == 85  # TODO sometimes it is 85


@pytest.mark.interceptor_test
def test_langchain_get_baseopenai_methods_to_intercept(setup_paig_plugin_with_app_config_file_name):
    langchain_llm_setup = privacera_shield.langchain_method_interceptor.LangChainMethodInterceptor(
        filter_in_classes=["BaseOpenAI"])
    langchain_llm_setup.find_all_methods_to_intercept()
    assert len(langchain_llm_setup.list_of_methods_to_intercept) == 4
    #    or len(
    # langchain_llm_setup.list_of_methods_to_intercept) == 2  # TODO sometimes it is 2
    langchain_llm_setup.undo_setup_interceptors()


@pytest.mark.e2e_test
def test_b_langchain_set_baseopenai_interceptor(setup_paig_plugin_with_app_config_file_name):
    privacera_shield.client.setup(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                  frameworks=["langchain"])

    # langchain_llm_setup = privacera_shield.langchain_callback.LangChainMethodInterceptor(
    #     filter_in_classes=["FakeListLLM"])
    # langchain_llm_setup.find_all_methods_to_intercept()
    # langchain_llm_setup.setup_interceptors(privacera_shield.core._paig_plugin)
    #
    # assert len(langchain_llm_setup.list_of_methods_to_intercept) == 1

    privacera_shield.client.set_current_user("user1")
    from langchain.llms.fake import FakeListLLM
    llm = FakeListLLM(responses=["response number 1", "response number 2", "response number 3"])
    for i in range(10):
        _logger.debug("will invoke llm(prompt)")
        _logger.debug(llm.invoke(f"prompt number {i}"))
        _logger.debug(llm.generate(prompts=[f"prompt number {i}"]))
    privacera_shield.client.clear()


def test_BaseLLMGenerateCallback(setup_paig_plugin_with_app_config_file_name):
    privacera_shield.client.setup(application_config_file=setup_paig_plugin_with_app_config_file_name,
                                  frameworks=["None"])

    class TestClass:
        def __init__(self, responses):
            self.responses = responses

        def generate(self, prompts):
            generations = [[Generation(text=response)] for response in self.responses]
            return LLMResult(generations=generations)

    privacera_shield.interceptor.wrap_method(privacera_shield.core._paig_plugin, TestClass, "generate",
                                             TestClass.generate,
                                             privacera_shield.langchain_method_interceptor.BaseLLMGenerateCallback)
    test_class = TestClass(["response number 1", "response number 2", "response number 3"])
    test_class.generate(["prompt number 1", "prompt number 2", "prompt number 3"])
