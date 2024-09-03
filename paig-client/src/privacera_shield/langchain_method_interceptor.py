import inspect
import logging
import time

from privacera_shield.backend import ShieldAccessRequest
from privacera_shield.exception import AccessControlException

from privacera_shield.interceptor import wrap_method, MethodIOCallback
from privacera_shield.model import ConversationType

_logger = logging.getLogger(__name__)
TRACE_LEVEL = 5


class LangChainMethodInterceptor:

    def __init__(self, **kwargs):
        self.filter_out_classes = ["LLM", "BaseLLM", "BaseLanguageModel", "Serializable", "RunnableSerializable",
                                   "BaseModel",
                                   "Representation", "ABC", "object",
                                   "Generic"] if "filter_out_classes" not in kwargs else kwargs["filter_out_classes"]
        self.filter_in_classes = [] if "filter_in_classes" not in kwargs else kwargs["filter_in_classes"]
        self.methods_to_intercept = ["_generate", "_agenerate", "_stream", "_astream",
                                     "_call"] if "methods_to_intercept" not in kwargs else kwargs[
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

        # now we want to go upwards in the class hierarchy and find the methods to intercept
        for cls_in_hierarchy in inspect.getmro(cls):
            cls_name = cls_in_hierarchy.__name__
            if cls_name in self.filter_out_classes:
                # skip because we want to filter this class out
                _logger.log(TRACE_LEVEL, f"skipping {cls_name} because it is in filter_out_classes")
                continue
            if self.filter_in_classes and cls_name not in self.filter_in_classes:
                # skip because we have a filter in place and this class is not in the filter
                _logger.log(TRACE_LEVEL, f"skipping {cls_name} because it is not in filter_in_classes")
                continue
            _logger.log(TRACE_LEVEL,
                        f"will process base-class__name__: {cls_name}, "
                        f"base-class.__module__: {cls_in_hierarchy.__module__} of {cls.__name__}")
            if cls_name in cls_to_methods:
                # _logger.debug(json.dumps(cls_to_methods[cls_in_hierarchy.__name__], indent=4))
                for m_name, method in cls_to_methods[cls_name]:
                    if m_name in self.methods_to_intercept:
                        to_intercept = (
                            cls_in_hierarchy.__module__, cls_name, m_name, cls_in_hierarchy, method)
                        if to_intercept not in self.list_of_methods_to_intercept:
                            self.list_of_methods_to_intercept.append(to_intercept)
                            _logger.log(TRACE_LEVEL, f"will intercept {to_intercept} for class {cls.__name__}")
            else:
                _logger.log(TRACE_LEVEL, f"No methods found for this base-class: {cls_name}")

    def find_all_methods_to_intercept(self):
        # import is hidden here so these dependencies will be loaded only when required
        import langchain.llms

        start_time = time.time()
        for type_str, get_class_method in langchain.llms.get_type_to_cls_dict().items():
            _logger.log(TRACE_LEVEL, f"Type: {type_str}")
            self.intercept_methods_for_class(get_class_method())
        end_time = time.time()
        _logger.debug(f"Time taken to intercept all methods: {end_time - start_time} seconds")
        _logger.log(TRACE_LEVEL, f"list_of_methods_to_intercept: {self.list_of_methods_to_intercept}")
        _logger.debug(f"total number of methods that will be intercepted is {len(self.list_of_methods_to_intercept)}")

    def setup_interceptors(self, paig_plugin):
        count = 0
        for module_name, class_name, method_name, cls, method in self.list_of_methods_to_intercept:
            if method_name in ["_generate", "_agenerate"]:
                wrap_method(paig_plugin, cls, method_name, method, BaseLLMGenerateCallback)
                count += 1
            elif method_name == "_call":
                wrap_method(paig_plugin, cls, method_name, method, LLMCallCallback)
                count += 1
            elif method_name in ["stream", "_astream"]:
                # TODO - need to add additional interceptors for other methods
                pass
        return count

    def undo_setup_interceptors(self):
        for module_name, class_name, method_name, cls, method in self.list_of_methods_to_intercept:
            setattr(cls, method_name, method)


class BaseLLMGenerateCallback(MethodIOCallback):
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

        Args:
            *args: Positional arguments passed to the method.
            **kwargs: Keyword arguments passed to the method.

        Returns:
            tuple: A tuple containing the updated args and kwargs.
        """

        access_request = ShieldAccessRequest(
            application_key=self.paig_plugin.get_application_key(),
            client_application_key=self.paig_plugin.get_client_application_key(),
            conversation_thread_id=self.paig_plugin.generate_conversation_thread_id(),
            request_id=self.paig_plugin.generate_request_id(),
            user_name=self.paig_plugin.get_current_user(),
            context=ShieldAccessRequest.create_request_context(paig_plugin=self.paig_plugin),
            request_text=args[0],
            conversation_type=ConversationType.PROMPT
        )

        access_result = self.paig_plugin.get_shield_client().is_access_allowed(access_request)

        # Throw exception if access is denied
        self.check_access(access_result)

        # We need to prepare updated arguments
        response_messages = access_result.get_response_messages()
        updated_input_args = []
        for message in response_messages:
            updated_input_args.append(message.get_response_text())

        updated_args = (updated_input_args,) + args[1:]

        return updated_args, kwargs

    def process_output(self, output):
        """
        Process the output values from the method callback.

        Args:
            output: The output from the method callback.

        Returns:
            Any: The processed output.
        """
        updated_generations = []

        if output.generations:
            generations = output.generations

            for generation in generations:

                request_text = []
                for s_generation in generation:
                    request_text.append(s_generation.text)

                access_request = ShieldAccessRequest(
                    application_key=self.paig_plugin.get_application_key(),
                    client_application_key=self.paig_plugin.get_client_application_key(),
                    conversation_thread_id=self.paig_plugin.generate_conversation_thread_id(),
                    request_id=self.paig_plugin.generate_request_id(),
                    user_name=self.paig_plugin.get_current_user(),
                    context=ShieldAccessRequest.create_request_context(paig_plugin=self.paig_plugin),
                    request_text=request_text,
                    conversation_type=ConversationType.REPLY
                )

                access_result = self.paig_plugin.get_shield_client().is_access_allowed(access_request)

                # Throw exception if access is denied
                self.check_access(access_result)

                # We need to prepare updated arguments
                response_messages = access_result.get_response_messages()
                updated_s_generations = []
                i = 0
                for message in response_messages:
                    existing_s_generation = generation[i]

                    updated_s_generation = existing_s_generation.copy()
                    updated_s_generation.text = message.get_response_text()
                    updated_s_generations.append(updated_s_generation)

                    i = i + 1

                updated_generations.append(updated_s_generations)

            output.generations = updated_generations

        return output


class ChainCallCallback(MethodIOCallback):
    def __init__(self, paig_plugin, cls, method):
        """
        Initialize the ChainCallCallback instance.

        Args:
            paig_plugin: The base plugin for the callback.
            cls: The class to which the callback is applied.
            method: The method to which the callback is applied.
        """
        super().__init__(paig_plugin, cls, method)

    def init(self):
        self.set_chain_recursive_call_count(0)
        self.set_conversation_thread_id("")

    def get_chain_recursive_call_count(self):
        return self.paig_plugin.get_current("chain_recursive_call_count")

    def set_chain_recursive_call_count(self, count):
        self.paig_plugin.set_current({
            "chain_recursive_call_count": count
        })

    def get_conversation_thread_id(self):
        return self.paig_plugin.get_current("conversation_thread_id")

    def set_conversation_thread_id(self, conversation_thread_id):
        self.paig_plugin.set_current({
            "conversation_thread_id": conversation_thread_id
        })

    def check_access(self, access_result):
        last_response_message = access_result.get_last_response_message()

        if not access_result.get_is_allowed():
            raise AccessControlException(last_response_message.get_response_text())

    def process_inputs(self, *args, **kwargs):
        """
        Process the input values from the method callback.

        Args:
            *args: Variable-length positional arguments.
            **kwargs: Variable-length keyword arguments.

        Returns:
            tuple: A tuple containing the updated *args and **kwargs.
        """
        chain_recursive_call_count = self.get_chain_recursive_call_count()
        if chain_recursive_call_count == 0:
            conversation_thread_id = self.paig_plugin.generate_conversation_thread_id()
            self.set_conversation_thread_id(conversation_thread_id)

            access_request = ShieldAccessRequest(
                application_key=self.paig_plugin.get_application_key(),
                client_application_key=self.paig_plugin.get_client_application_key(),
                conversation_thread_id=conversation_thread_id,
                request_id=self.paig_plugin.generate_request_id(),
                user_name=self.paig_plugin.get_current_user(),
                context=ShieldAccessRequest.create_request_context(paig_plugin=self.paig_plugin),
                request_text=args[0]["question"],
                conversation_type=ConversationType.PROMPT
            )

            access_result = self.paig_plugin.get_shield_client().is_access_allowed(access_request)

            # Throw exception if access is denied
            self.check_access(access_result)

            # We need to prepare updated arguments
            last_response_message = access_result.get_last_response_message()
            args[0]["question"] = last_response_message.get_response_text()

        chain_recursive_call_count += 1
        self.set_chain_recursive_call_count(chain_recursive_call_count)

        return args, kwargs

    def process_output(self, output):
        """
        Process the output values from the method callback.

        Args:
            output: The output from the method callback.

        Returns:
            Any: The updated output.
        """
        chain_recursive_call_count = self.get_chain_recursive_call_count()
        chain_recursive_call_count -= 1
        self.set_chain_recursive_call_count(chain_recursive_call_count)

        if chain_recursive_call_count == 0:
            self.set_conversation_thread_id("")

        return output


class LLMCallCallback(MethodIOCallback):
    """
    Callback that intercepts LLM._call()

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

        Args:
            *args: Positional arguments passed to the method.
            **kwargs: Keyword arguments passed to the method.

        Returns:
            tuple: A tuple containing the updated args and kwargs.
        """

        _logger.debug(f"LLMCallCallback.process_inputs with args={args}, kwargs={kwargs}")
        access_request = ShieldAccessRequest(
            application_key=self.paig_plugin.get_application_key(),
            client_application_key=self.paig_plugin.get_client_application_key(),
            conversation_thread_id=self.paig_plugin.generate_conversation_thread_id(),
            request_id=self.paig_plugin.generate_request_id(),
            user_name=self.paig_plugin.get_current_user(),
            context=ShieldAccessRequest.create_request_context(paig_plugin=self.paig_plugin),
            request_text=[args[0]],
            conversation_type=ConversationType.PROMPT
        )

        access_result = self.paig_plugin.get_shield_client().is_access_allowed(access_request)

        # Throw exception if access is denied
        self.check_access(access_result)

        # We need to prepare updated arguments
        response_messages = access_result.get_response_messages()
        updated_input_args = response_messages[0].response_text
        updated_args = (updated_input_args,) + args[1:]

        return updated_args, kwargs

    def process_output(self, output):
        """
        Process the output values from the method callback.

        Args:
            output: The output from the method callback.

        Returns:
            Any: The processed output.
        """
        access_request = ShieldAccessRequest(
            application_key=self.paig_plugin.get_application_key(),
            client_application_key=self.paig_plugin.get_client_application_key(),
            conversation_thread_id=self.paig_plugin.generate_conversation_thread_id(),
            request_id=self.paig_plugin.generate_request_id(),
            user_name=self.paig_plugin.get_current_user(),
            context=ShieldAccessRequest.create_request_context(paig_plugin=self.paig_plugin),
            request_text=[output],
            conversation_type=ConversationType.REPLY
        )

        access_result = self.paig_plugin.get_shield_client().is_access_allowed(access_request)

        # Throw exception if access is denied
        self.check_access(access_result)

        # We need to prepare updated arguments
        response_messages = access_result.get_response_messages()
        return response_messages[0].response_text
