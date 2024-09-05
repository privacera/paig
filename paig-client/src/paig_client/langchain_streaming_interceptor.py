import copy
import inspect
import logging
import time

from paig_client.exception import AccessControlException

from paig_client.interceptor import wrap_method, MethodIOCallback

_logger = logging.getLogger(__name__)
TRACE_LEVEL = 5


class LangChainStreamingInterceptor:

    def __init__(self, **kwargs):
        self.methods_to_intercept = ["on_llm_new_token"] if "methods_to_intercept" not in kwargs else kwargs[
            "methods_to_intercept"]
        self.list_of_methods_to_intercept = []

    def intercept_methods_for_class(self, cls):
        cls_to_methods = dict()  # key: class name, value: list of methods
        for method_name, method in inspect.getmembers(cls, callable):
            if method_name.startswith("__"):
                continue
            qual_name = method.__qualname__
            cls_name_of_method = qual_name.split(".")[0]
            cls_to_methods.setdefault(cls_name_of_method, []).append((method_name, method))
            if _logger.isEnabledFor(TRACE_LEVEL):
                _logger.log(TRACE_LEVEL,
                            f"{cls} has method {method_name} with "
                            f"qual_name {qual_name} and cls_name_of_method {cls_name_of_method}")

        cls_name = cls.__name__
        if cls_name in cls_to_methods:
            for m_name, method in cls_to_methods[cls_name]:
                if m_name in self.methods_to_intercept:
                    to_intercept = (
                        cls.__module__, cls_name, m_name, cls, method)
                    if to_intercept not in self.list_of_methods_to_intercept:
                        self.list_of_methods_to_intercept.append(to_intercept)
                        _logger.log(TRACE_LEVEL, f"will intercept {to_intercept} for class {cls.__name__}")
        else:
            _logger.log(TRACE_LEVEL, f"No methods found for this base-class: {cls_name}")

    def find_all_methods_to_intercept(self):
        # import is hidden here so these dependencies will be loaded only when required

        start_time = time.time()
        for type_str, get_class_method in self.get_type_to_cls_dict().items():
            _logger.log(TRACE_LEVEL, f"Type: {type_str}")
            self.intercept_methods_for_class(get_class_method)
        end_time = time.time()
        _logger.debug(f"Time taken to intercept all methods: {end_time - start_time} seconds")
        _logger.log(TRACE_LEVEL, f"list_of_methods_to_intercept: {self.list_of_methods_to_intercept}")
        _logger.debug(f"total number of methods that will be intercepted is {len(self.list_of_methods_to_intercept)}")

    def setup_interceptors(self, paig_plugin):
        count = 0
        for module_name, class_name, method_name, cls, method in self.list_of_methods_to_intercept:
            if method_name in ["on_llm_new_token"]:
                wrap_method(paig_plugin, cls, method_name, method, LangchainStreamingCallback)
                count += 1
        return count

    def undo_setup_interceptors(self):
        for module_name, class_name, method_name, cls, method in self.list_of_methods_to_intercept:
            setattr(cls, method_name, method)

    def get_type_to_cls_dict(self):
        def get_callback_manager_for_llm_run_import():
            from langchain_core.callbacks.manager import CallbackManagerForLLMRun

            return CallbackManagerForLLMRun

        type_to_cls_dict = {
            "CallbackManagerForLLMRun": get_callback_manager_for_llm_run_import()
        }

        return type_to_cls_dict


class LangchainStreamingCallback(MethodIOCallback):
    """
    Callback class for generating Long-Lived Model (LLM) data with access control.

    This class extends MethodIOCallback and adds access control to the LLM data generation process.
    """

    def __init__(self, paig_plugin, cls, method):
        """
        Initialize the BaseLLMGenerateCallback instance.

        Args:
            paig_plugin: The base plugin for the callback.
            cls: The class to which the callback is applied.
            method: The method to which the callback is applied.
        """
        super().__init__(paig_plugin, cls, method)

    def init(self):
        pass

    def check_access(self, access_result):
        last_response_message = access_result.get_last_response_message()

        if not access_result.get_is_allowed():
            raise AccessControlException(last_response_message.get_response_text())

    def process_inputs(self, *args, **kwargs):
        """
        Process the input values from the method callback.

        This method processes the input values received as positional and keyword arguments,
        updates them as necessary, and returns the updated arguments and keyword arguments.

        Args:
            *args: Positional arguments passed to the method.
            **kwargs: Keyword arguments passed to the method.

        Returns:
            tuple: A tuple containing the updated args and kwargs.
        """

        # Extract the LLM reply token from positional arguments
        llm_reply_token = args[0]

        # Get an instance of the LLMAStreamAccessChecker
        llm_stream_access_checker = self.paig_plugin.get_llm_stream_access_checker()

        # Copy keyword arguments to avoid modification of the original dictionary
        updated_kwargs = kwargs.copy()
        if not llm_stream_access_checker.is_first_reply_token_received:
            """
            When processing tokens received from the Language Model (LLM), it's important to handle the first token differently due to how it's stored in the full reply variable.
            For subsequent tokens, a simple copy operation is sufficient for processing. However, for the first token, a deepcopy is necessary to prevent modifying the original token stored in the full reply variable.
            This is because the first token is directly stored in the full reply variable, and modifying it without deep copying would alter the original token stored in full reply.
            Example:
            Suppose tokens are received sequentially from the LLM: "Nancy", "is", "the", "first", "customer", ".".
            When processing the first token "Nancy", deepcopy is used to ensure that any modifications made during processing don't affect the original token stored in full reply.
            For subsequent tokens ("is", "the", "first", "customer", "."), a simple copy operation can be used as they are processed individually and don't have the same reference issue as the first token.
            """
            llm_stream_access_checker.is_first_reply_token_received = True
            updated_kwargs = copy.deepcopy(kwargs)

        # Check access for the LLM reply token using LLMAStreamAccessChecker
        shield_authorized_reply = llm_stream_access_checker.check_access(llm_reply_token)

        # Update positional arguments with shield authorized reply
        updated_args = (shield_authorized_reply,) + args[1:]

        # Copy keyword arguments to avoid modification of the original dictionary
        # Update 'text' attribute of the 'chunk' object in keyword arguments with shield authorized reply
        # The streaming library performed a pull for messages or tokens from the server,
        # but did not receive any chunk data. Then `updated_kwargs` may not contain chunk key in dictionary.
        if "chunk" in updated_kwargs:
            updated_kwargs["chunk"].text = shield_authorized_reply

        return updated_args, updated_kwargs