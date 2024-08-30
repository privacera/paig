import json
import os
import logging
import sys

from opensearchpy import OpenSearch, RequestsHttpConnection, exceptions
from core import constants
from core.utils import format_to_root_path
from core.config import load_config_file

Config = load_config_file()

OPEN_SEARCH_INDEX_PAIG_ADMIN_AUDITS = "paig_admin_audits"
OPEN_SEARCH_INDEX_PAIG_SHIELD_AUDITS = "paig_shield_audits"
OBJECT_STATE_PREFIX = "objectState."
OBJECT_STATE_PREVIOUS_PREFIX = "objectState.previous."
KEYWORD_POSTFIX = ".keyword"
PARTIAL_MATCH_POSTFIX = ".partial"

logger = logging.getLogger(__name__)


def get_opensearch_client(host: str, auth: tuple):
    return OpenSearch(
        hosts=host,
        http_auth=auth,
        http_compress=True,
        use_ssl=True,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
        connection_class=RequestsHttpConnection,
        pool_maxsize=20
    )


class OpenSearchClient:
    def __init__(self):
        self.opensearch_conf = Config['opensearch']
        host = self.opensearch_conf.get('endpoint')
        username = self.opensearch_conf.get('username')
        password = self.opensearch_conf.get('secret')
        auth = (username, password)
        self.opensearch_client = get_opensearch_client(host, auth)
        self._initialize()

    def _initialize(self):
        self._init_admin_audit_index()
        self._init_access_audit_index()

    def _init_access_audit_index(self):
        self.access_audit_index = self.opensearch_conf.get('access_audit_index', f"{OPEN_SEARCH_INDEX_PAIG_SHIELD_AUDITS}_{constants.DEFAULT_TENANT_ID}")
        self._init_access_audit_template()
        if not self.opensearch_client.indices.exists(index=self.access_audit_index):
            self.create_index(self.access_audit_index)

    def _init_admin_audit_index(self):
        self.admin_audit_index = self.opensearch_conf.get('admin_audit_index',
                                                          f"{OPEN_SEARCH_INDEX_PAIG_ADMIN_AUDITS}_{constants.DEFAULT_TENANT_ID}")
        self._init_admin_audit_template()
        if not self.opensearch_client.indices.exists(index=self.admin_audit_index):
            self.create_index(self.admin_audit_index)

    def _init_admin_audit_template(self):
        template_name = self.opensearch_conf.get('admin_audit_template', f"{OPEN_SEARCH_INDEX_PAIG_ADMIN_AUDITS}_template")
        template_file_path = self.opensearch_conf.get('admin_audit_template_file', 'api/audit/opensearch_service/resources/admin_audit_template.json')
        self.check_and_create_template(template_name, template_file_path, self.admin_audit_index)

    def _init_access_audit_template(self):
        template_name = self.opensearch_conf.get('access_audit_template', f"{OPEN_SEARCH_INDEX_PAIG_SHIELD_AUDITS}_template")
        template_file_path = self.opensearch_conf.get('access_audit_template_file', 'api/audit/opensearch_service/resources/access_audit_template.json')
        self.check_and_create_template(template_name, template_file_path, self.access_audit_index)

    def get_client(self):
        return self.opensearch_client

    def get_index_name(self, is_admin_audits):
        if is_admin_audits:
            return self.admin_audit_index
        return self.access_audit_index

    def create_index(self, index_name):
        logger.info(f"Creating index: {index_name}")
        self.opensearch_client.indices.create(index=index_name, ignore=400)

    def delete_index(self, index_name):
        logger.info(f"Deleting index: {index_name}")
        self.opensearch_client.indices.delete(index=index_name, ignore=[400, 404])

    def get_template(self, template_name):
        try:
            return self.opensearch_client.indices.get_index_template(name=template_name)
        except exceptions.NotFoundError:
            return None
        except exceptions.AuthenticationException:
            sys.exit("Authentication failed. Please check the opesearch credentials provided in config file")

    def create_template(self, template_name, template_body):
        try:
            self.opensearch_client.indices.put_index_template(name=template_name, body=template_body)
        except exceptions.RequestError as e:
            logger.error(f"Error while creating template: {e}")
            raise e

    def check_and_create_template(self, template_name, template_file_path, exact_index_name):
        templated_file_path: str = format_to_root_path(template_file_path)
        if not os.path.exists(templated_file_path):
            logger.error(f"Template file not found: {templated_file_path}")
            raise FileNotFoundError(f"Template file not found: {templated_file_path}")
        with open(templated_file_path, 'r') as file:
            template_body = json.load(file)
        # Append or set the index_patterns field to include the exact index name
        if 'index_patterns' in template_body:
            template_body['index_patterns'].append(exact_index_name)
        else:
            template_body['index_patterns'] = [exact_index_name]
        if not self.get_template(template_name):
            logger.info(f"Creating template: {template_name}")
            self.create_template(template_name, template_body)
        else:
            logger.info(f"Template already exists: {template_name}")


