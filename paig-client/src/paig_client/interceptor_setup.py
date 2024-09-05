import logging

from .message import InfoMessage, WarningMessage

_logger = logging.getLogger(__name__)


def setup(paig_plugin):
    interceptor_list = []
    for framework in paig_plugin.get_frameworks_to_intercept():
        if framework.lower() == 'langchain':
            from .langchain_callback import setup_langchain_interceptors
            setup_langchain_interceptors(interceptor_list, paig_plugin)
        elif framework.lower() == 'milvus':
            from .milvus_method_interceptor import setup_milvus_interceptors
            setup_milvus_interceptors(interceptor_list, paig_plugin)
        elif framework.lower() == 'opensearch':
            from .opensearch_method_interceptor import setup_opensearch_interceptors
            setup_opensearch_interceptors(interceptor_list, paig_plugin)
        elif framework.lower() == 'none':
            _logger.info(InfoMessage.NO_FRAMEWORKS_TO_INTERCEPT)
        else:
            _logger.warning(WarningMessage.FRAMEWORK_NOT_SUPPORTED.format(framework=framework))
    return interceptor_list


def clear(interceptor_list):
    for interceptor in interceptor_list:
        interceptor.undo_setup_interceptors()
