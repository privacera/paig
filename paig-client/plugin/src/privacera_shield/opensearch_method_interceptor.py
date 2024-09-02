import copy
import inspect
import logging
import time
import ast

from .interceptor import wrap_method, MethodIOCallback
from .message import InfoMessage

_logger = logging.getLogger(__name__)
TRACE_LEVEL = 5


def setup_opensearch_interceptors(interceptor_list, paig_plugin):
    opensearch_interceptor = OpenSearchClientInterceptorSetup()
    opensearch_interceptor.find_all_methods_to_intercept()
    count = opensearch_interceptor.setup_interceptors(paig_plugin)
    if _logger.isEnabledFor(logging.INFO):
        _logger.info(InfoMessage.OPENSEARCH_INITIALIZED.format(count=count))
    interceptor_list.append(opensearch_interceptor)


class OpenSearchClientInterceptorSetup:

    def __init__(self, **kwargs):
        self.filter_out_classes = [] if "filter_out_classes" not in kwargs else kwargs["filter_out_classes"]
        self.filter_in_classes = ["OpenSearchVectorSearch"] if "filter_in_classes" not in kwargs else kwargs["filter_in_classes"]
        self.methods_to_intercept = ["_raw_similarity_search_with_score", "_raw_similarity_search_with_score_by_vector"] if "methods_to_intercept" not in kwargs else kwargs[
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
            if method_name in self.methods_to_intercept:
                wrap_method(paig_plugin, cls, method_name, method, OpenSearchFilterCallback)
                count += 1
        return count

    def undo_setup_interceptors(self):
        for module_name, class_name, method_name, cls, method in self.list_of_methods_to_intercept:
            setattr(cls, method_name, method)

    def get_type_to_cls_dict(self):
        def get_langchain_opensearch_import():
            from langchain.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
            return OpenSearchVectorSearch

        def get_langchain_community_opensearch_import():
            from langchain_community.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
            return OpenSearchVectorSearch

        type_to_cls_dict = {}

        try:
            # Keeping this for backward compatibility
            langchain_opensearch_class = get_langchain_opensearch_import()
            type_to_cls_dict["langchain_opensearch"] = langchain_opensearch_class
        except ImportError:
            _logger.warning("langchain.vectorstores.opensearch_vector_search.OpenSearchVectorSearch not found")

        try:
            langchain_community_opensearch_class = get_langchain_community_opensearch_import()
            type_to_cls_dict["langchain_community_opensearch"] = langchain_community_opensearch_class
        except ImportError:
            _logger.warning("langchain_community.vectorstores.opensearch_vector_search.OpenSearchVectorSearch not found")

        return type_to_cls_dict


class OpenSearchFilterCallback(MethodIOCallback):
    """
    Callback class for opensearch and adding row filter expression dynamically.

    This class extends MethodIOCallback and adds access control and row filter expression dynamically.
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

    def process_inputs(self, *args, **kwargs):
        """
        Process the input values from the method callback.

        Args:
            *args: Positional arguments passed to the method.
            **kwargs: Keyword arguments passed to the method.

        Returns:
            tuple: A tuple containing the updated args and kwargs.
        """

        _logger.debug(f"OpenSearchFilterCallback.process_inputs with args={args}, kwargs={kwargs}")

        # In case if there is no policy to be evaluated for current user then we will get blank filter
        shield_filter_expr = self.paig_plugin.get_vector_db_filter_expression()

        updated_kwargs = copy.deepcopy(kwargs)

        # Setting the received shield_filter_expr inside context, so we can pass it for auditing when sending next
        # request for prompt authorization
        if shield_filter_expr != "":
            self.paig_plugin.set_current(vector_db_filter_expr=shield_filter_expr)

            # TODO Currently not adding existing filter with ours, just overriding with what we get from shield
            updated_kwargs["filter"] = ast.literal_eval(shield_filter_expr)

        return args, updated_kwargs

    def process_output(self, output):
        """
        Process the output values from the method callback.

        Args:
            output: The output from the method callback.

        Returns:
            Any: The processed output.
        """
        return output
