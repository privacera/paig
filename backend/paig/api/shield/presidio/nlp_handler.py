"""
Module: NLPHandler

This module provides a singleton NLPHandler class for managing Natural Language Processing (NLP) engines.

Classes:
    NLPHandler: Singleton class for handling NLP engines.

Imports:
    os: Provides a way to interact with the operating system.
    NlpEngineProvider: Provides NLP engine creation and management.
    Lock: Provides a thread synchronization primitive.

"""
import logging
import os
from presidio_analyzer.nlp_engine import NlpEngineProvider
from threading import Lock

from core.utils import format_to_root_path
from api.shield.utils import config_utils


class NLPHandler:
    """
   Singleton class for managing Natural Language Processing (NLP) engines.

   Attributes:
       _instance (NLPHandler): Singleton instance of NLPHandler.
       _lock (Lock): Lock for thread safety.
       nlp_engine: Instance of the NLP engine.

   """
    _instance = None
    _lock = Lock()
    nlp_engine = None

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ method to ensure singleton pattern.

        Returns:
            NLPHandler: Singleton instance of NLPHandler.

        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(NLPHandler, cls).__new__(cls)
                cls._instance.init_singleton()
        return cls._instance

    def init_singleton(self):
        """
        Initialize the singleton instance by creating the NLP engine.

        """
        presidio_logger = logging.getLogger("presidio-analyzer")
        presidio_log_level = logging.getLevelName(config_utils.get_property_value("presidio_log_level", "INFO"))
        presidio_logger.setLevel(presidio_log_level)
        self.nlp_engine = self.get_nlp_provider().create_engine()

    @staticmethod
    def get_nlp_provider():
        """
        Get the NLP engine provider.

        Returns:
            NlpEngineProvider: NLP engine provider.

        """
        custom_nlp_file = format_to_root_path("api/shield/cust-conf/presidio_nlp_config.yaml")
        if os.path.exists(custom_nlp_file):
            return NlpEngineProvider(conf_file=custom_nlp_file)
        else:
            return NlpEngineProvider(conf_file=format_to_root_path('api/shield/conf/presidio_nlp_config.yaml'))

    def get_engine(self):
        """
        Get the NLP engine.

        Returns:
            NlpEngine: NLP engine instance.

        """
        return self.nlp_engine
