from fastapi import HTTPException
from opensearchpy.exceptions import NotFoundError, OpenSearchException
import logging

from api.audit.opensearch_service.opensearch_client import OpenSearchClient
from api.audit.factory.service_interface import DataServiceInterface
from core.controllers.paginated_response import create_pageable_response
from api.audit.opensearch_service.opensearch_util import build_query, convert_to_sorted_dict, \
    build_search_request_with_aggregations, extract_search_response_aggregations
from core.utils import SingletonDepends

logger = logging.getLogger(__name__)


class OpenSearchService(DataServiceInterface):
    def __init__(self, opensearch_client: OpenSearchClient):
        self.opensearch_client = opensearch_client

    async def create_access_audit(self, access_audit_params):
        if not isinstance(access_audit_params, dict):
            access_audit_params = access_audit_params.dict(by_alias=True)
        await self._insert_access_audit(access_audit_params, is_admin_audits=None)

    async def _insert_access_audit(self, access_audit_params, is_admin_audits):
        index_name = self.opensearch_client.get_index_name(is_admin_audits)
        try:
            response = self.opensearch_client.get_client().index(index=index_name, body=access_audit_params)
        except OpenSearchException as e:
            logger.error(f'OpenSearch exception occurred: {str(e)}')
            raise HTTPException(status_code=500, detail="OpenSearch exception occurred")
        except Exception as e:
            logger.error(f'Exception occurred: {str(e)}')
            raise HTTPException(status_code=500, detail=str(e))

    async def get_access_audits(self, include_query, exclude_query, page, size, sort, from_time, to_time):
        return self.get_audits(include_query, exclude_query, page, size, sort, from_time, to_time, None)

    def get_audits(self, include_query, exclude_query, page, size, sort, from_time, to_time,
                         is_admin_audits):

        index_name = self.opensearch_client.get_index_name(is_admin_audits)
        offset = page * size

        query_body = {
            "query": build_query(include_query, exclude_query, from_time, to_time, is_admin_audits),
            "from": offset,
            "size": size,
            "sort": convert_to_sorted_dict(sort)
        }

        try:
            response = self.opensearch_client.get_client().search(body=query_body, index=index_name)
        except NotFoundError:
            logger.error(f'Audit index does not exist: {index_name}')
            return create_pageable_response([], 0, 0, size, [])
        except OpenSearchException as e:
            logger.error(f'OpenSearch exception occurred while getting audits: {str(e)}')
            raise HTTPException(status_code=500, detail="OpenSearch exception occurred")
        except Exception as e:
            logger.error(f'Exception occurred while getting audits: {str(e)}')
            raise HTTPException(status_code=500, detail=str(e))

        hits = response['hits']['hits']
        total = response['hits']['total']['value']
        audits = [hit['_source'] for hit in hits]

        return create_pageable_response(audits, total, page, size, [])

    async def get_usage_counts(self, include_query, from_time, to_time):
        return self.get_counts("result", include_query, from_time, to_time, None, None, None, False)

    async def get_trait_counts_by_application(self, include_query, from_time, to_time):
        return self.get_counts("traits,applicationName", include_query, from_time, to_time, None, None, None, False)

    async def get_access_data_counts(self, include_query, from_time, to_time, interval):
        return self.get_counts("result", include_query, from_time, to_time, interval, None, None, False)

    async def get_user_id_counts(self, size):
        return self.get_counts("userId", None, None, None, None, size, None, False)

    async def get_app_name_counts(self, size):
        return self.get_counts("applicationName", None, None, None, None, size, None, False)

    async def get_app_name_by_user_id(self, include_query, from_time, to_time):
        return self.get_counts("applicationName,userId", include_query, from_time, to_time, None, None, True, False)

    async def get_top_users_count(self, include_query, size, from_time, to_time):
        return self.get_counts("userId", include_query, from_time, to_time, None, size, None, False)

    async def get_unique_user_id_count(self, include_query, from_time, to_time):
        return self.get_counts("userId", include_query, from_time, to_time, None, None, True, False)

    async def get_unique_trait_count(self, include_query, from_time, to_time):
        return self.get_counts("traits", include_query, from_time, to_time, None, None, None, False)

    async def get_activity_trend_counts(self, include_query, from_time, to_time, interval):
        return self.get_counts("tenantId", include_query, from_time, to_time, interval, None, None, False)

    async def get_admin_audits(self, include_query, page, size, sort, from_time, to_time):
        return self.get_audits(include_query, None, page, size, sort, from_time, to_time, True)

    async def get_admin_audits_count(self, include_query, size, from_time, to_time, group_by, cardinality, interval):
        return self.get_counts(group_by, include_query, from_time, to_time, interval, size, cardinality, True)

    def get_counts(self, group_by, include_query, from_time, to_time, interval, size, cardinality,
                   is_admin_audits):
        index_name = self.opensearch_client.get_index_name(is_admin_audits)

        query_body = {
            "size": 0,
            "query": build_query(include_query, None, from_time, to_time, is_admin_audits)
        }

        query_body = build_search_request_with_aggregations(group_by, interval, size, cardinality, is_admin_audits, query_body)

        aggregations = {}
        try:
            response = self.opensearch_client.get_client().search(body=query_body, index=index_name)
            aggregations = response.get('aggregations', {})
        except NotFoundError:
            logger.error(f'Index does not exist: {index_name}')
            return {}
        except OpenSearchException as e:
            logger.error(f'OpenSearch exception occurred while getting counts: {str(e)}')
            raise HTTPException(status_code=500, detail="OpenSearch exception occurred")
        except Exception as e:
            logger.error(f'Exception occurred while getting counts: {str(e)}')
            raise HTTPException(status_code=500, detail=str(e))

        return extract_search_response_aggregations(interval, aggregations)


def get_opensearch_service(opensearch_client: OpenSearchClient = SingletonDepends(OpenSearchClient)):
    return OpenSearchService(opensearch_client=opensearch_client)
