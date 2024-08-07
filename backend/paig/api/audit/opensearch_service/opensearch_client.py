from opensearchpy import OpenSearch, RequestsHttpConnection

from core.config import load_config_file

Config = load_config_file()

TENANT_ID =
OPEN_SEARCH_INDEX_PAIG_ADMIN_AUDITS = "paig_admin_audits"
OPEN_SEARCH_INDEX_PAIG_SHIELD_AUDITS = "paig_shield_audits"
OBJECT_STATE_PREFIX = "objectState."
OBJECT_STATE_PREVIOUS_PREFIX = "objectState.previous."
KEYWORD_POSTFIX = ".keyword"
PARTIAL_MATCH_POSTFIX = ".partial"


def get_opensearch_client(host: str, auth: tuple):
    return OpenSearch(
        hosts=[{'host': host, 'port': 443}],
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
        opensearch_conf = Config['opensearch']
        host = opensearch_conf.get('endpoint')
        username = opensearch_conf.get('username')
        password = opensearch_conf.get('secret')
        auth = (username, password)

        self.opensearch_client = get_opensearch_client(host, auth)

    def get_client(self):
        return self.opensearch_client
