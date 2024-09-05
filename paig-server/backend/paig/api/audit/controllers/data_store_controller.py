import importlib

from core.utils import SingletonDepends
from core.config import load_config_file


config = load_config_file()


def get_service_instance():
    audit_storage_datasource = config.get("audit_storage_datasource", "RDS")
    class_type = audit_storage_datasource.upper()
    class_map = {
        "RDS": "api.audit.RDS_service.rds_service.get_rds_service",
        "OPENSEARCH": "api.audit.opensearch_service.opensearch_service.get_opensearch_service"
    }
    module_name, function_name = class_map[class_type].rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, function_name)


class DataStoreController:

    def __init__(self, service=SingletonDepends(get_service_instance())):
        self.service = service

    def get_service(self):
        return self.service
