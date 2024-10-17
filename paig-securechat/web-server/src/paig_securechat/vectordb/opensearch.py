import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.helpers import bulk
import logging
import json

logger = logging.getLogger(__name__)


def get_opensearch_cluster_client(hosts, user, password, index):
    opensearch_client = OpenSearch(
        hosts=hosts,
        http_auth=(user, password),
        index_name=index,
        use_ssl=True,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
        timeout=30
    )
    return opensearch_client


def put_bulk_in_opensearch(list, opensearch_client):
    logger.info(f"Putting {len(list)} documents in OpenSearch")
    success, failed = bulk(opensearch_client, list)
    return success, failed


def check_opensearch_index(opensearch_client, index_name):
    return opensearch_client.indices.exists(index=index_name)


def create_index(opensearch_client, index_name):
    settings = {
        "settings": {
            "index": {
                "knn": True,
                "knn.space_type": "cosinesimil"
            }
        }
    }
    response = opensearch_client.indices.create(index=index_name, body=settings)
    return bool(response['acknowledged'])


def create_index_mapping(opensearch_client, index_name):
    response = opensearch_client.indices.put_mapping(
        index=index_name,
        body={
            "properties": {
                "vector_field": {
                    "type": "knn_vector",
                    "dimension": 1536
                },
                "text": {
                    "type": "keyword"
                }
            }
        }
    )
    return bool(response['acknowledged'])


def delete_opensearch_index(opensearch_client, index_name):
    logger.info(f"Trying to delete index {index_name}")
    try:
        response = opensearch_client.indices.delete(index=index_name)
        logger.info(f"Index {index_name} deleted")
        return response['acknowledged']
    except Exception as e:
        logger.error(f"Index {index_name} not found, nothing to delete")
        return True


def get_secret(secret_prefix, region):
    client = boto3.client('secretsmanager', region_name=region)
    secret_arn = locate_secret_arn(secret_prefix, client)
    secret_value = client.get_secret_value(SecretId=secret_arn)
    return secret_value['SecretString']


def locate_secret_arn(secret_tag_value, client):
    response = client.list_secrets(
        Filters=[
            {
                'Key': 'tag-key',
                'Values': ['Name']
            },
            {
                'Key': 'tag-value',
                'Values': [secret_tag_value]
            }
        ]
    )
    return response['SecretList'][0]['ARN']


def get_opensearch_endpoint(domain_name, region):
    client = boto3.client('es', region_name=region)
    response = client.describe_elasticsearch_domain(
        DomainName=domain_name
    )
    logger.info(f"get_opensearch_endpoint domain={domain_name}, region={region}, \nresponse={response}")
    return response['DomainStatus']['Endpoints']['vpc']

