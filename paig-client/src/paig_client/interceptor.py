import inspect
import logging
from abc import abstractmethod

_logger = logging.getLogger(__name__)


def intercept_method(paig_plugin, cls, method_name, callback):
    """
    Intercept and modify multiple methods with a callback.

    Args:
        paig_plugin: The base plugin for the callback.
        cls: The class containing the methods to be intercepted.
        method_name: Method name to intercept.
        callback: The callback to apply to intercepted methods.
    """
    intercept_methods(paig_plugin, cls, [method_name], callback)


def intercept_methods(paig_plugin, cls, method_names, callback):
    """
    Intercept and modify a specific method with a callback.

    Args:
        paig_plugin: The base plugin for the callback.
        cls: The class containing the method to be intercepted.
        method_names (list): List of method names to intercept.
        callback: The callback to apply to the intercepted method.
    """
    for method_name, method in inspect.getmembers(cls, callable):
        if method_name in method_names:
            method = method
            wrap_method(paig_plugin, cls, method_name, method, callback)


def wrap_method(paig_plugin, cls, method_name, method, callback):
    def __wrap__(my_callback):
        def wrapper(self, *args, **kwargs):
            # Call inputs processor
            updated_args, updated_kwargs = my_callback.callback_input(*args, **kwargs)

            # Call the actual method
            output = my_callback.method(self, *updated_args, **updated_kwargs)

            # Call output processor
            updated_output = my_callback.callback_output(output)

            return updated_output

        return wrapper

    if method is None:
        _logger.debug(f"The provided method {method_name} is not found within {cls}")
    else:
        _logger.debug(f"The provided method {method_name} inside class {cls} initialized with interceptor")
        # Replace the original method with the wrapped method
        setattr(cls, method_name, __wrap__(callback(paig_plugin, cls, method)))


class MethodIOCallback:
    """
    Base class for defining method callbacks with input and output processing.
    """

    def __init__(self, paig_plugin, cls, method):
        """
        Initialize the MethodIOCallback instance.

        Args:
            paig_plugin: The base plugin for the callback.
            cls: The class to which the callback is applied.
            method: The method to which the callback is applied.
        """
        self.paig_plugin = paig_plugin
        self.cls = cls
        self.method = method

    @abstractmethod
    def init(self):
        """
        Initialize the callback. Subclasses should implement this method.

        This method is called once during the first usage of the callback.
        """
        pass

    def callback_input(self, *args, **kwargs):
        """
        Callback method for processing input arguments before calling the actual method.

        Args:
            *args: Variable-length positional arguments.
            **kwargs: Variable-length keyword arguments.

        Returns:
            Tuple: A tuple containing updated *args and **kwargs after processing inputs.
        """
        self.check_and_init()
        return self.process_inputs(*args, **kwargs)

    def check_and_init(self):
        init_key = self.__class__.__name__ + "_init"
        if not self.paig_plugin.get_current(init_key, False):
            self.init()
            self.paig_plugin.set_current(**{init_key: True})

    def callback_output(self, output):
        """
        Callback method for processing the output of the actual method.

        Args:
            output: The output of the actual method.

        Returns:
            Any: The processed output.
        """
        self.check_and_init()
        return self.process_output(output)

    @abstractmethod
    def process_inputs(self, *args, **kwargs):
        """
        Process the input values from the method callback.

        Args:
            *args: Positional arguments passed to the method.
            **kwargs: Keyword arguments passed to the method.
        """
        pass

    @abstractmethod
    def process_output(self, output):
        """
        Process the output value from the method callback.

        Args:
            output: The return value of the method.
        """
        pass
