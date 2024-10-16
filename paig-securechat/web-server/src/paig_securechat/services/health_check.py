from sqlalchemy import text
import logging
from vectordb.opensearch import get_opensearch_cluster_client, get_opensearch_endpoint, get_secret
from vectordb.vector_utils import opensearch_indexes
logger = logging.getLogger(__name__)


async def get_db_health_check(session) -> (bool, str):
    try:
        await session.execute(text("SELECT 1"))
        logger.info("Database is healthy")
    except Exception as e:
        logger.error(f"Error in get_db_health_check: {e}")
        return False, f"Database service is down due to reason:: {str(e)}"
    return True, ""


async def get_opensearch_health_check(config) -> (bool, str):
    try:
        if opensearch_indexes:
            opensearch_conf = config["opensearch"]
            user = opensearch_conf.get("user")
            password = opensearch_conf.get("password")
            domain_name = opensearch_conf.get("domain_name")
            region = opensearch_conf.get("region")
            hosts = opensearch_conf.get("hosts")
            if domain_name and region:
                user = domain_name
                password = get_secret(domain_name, region)
                hosts = get_opensearch_endpoint(domain_name, region)
            for index in opensearch_indexes:
                if user and password and hosts and index:
                    opensearch_client = get_opensearch_cluster_client(hosts, user, password, index)
                    health_check_response = opensearch_client.cluster.health()
                    logger.info(
                        f"Open health check response for index name {index} :: {health_check_response}")
                    logger.info(
                        f"Open search health status for index name {index} :: {health_check_response['status']}")
                    if health_check_response["status"].lower() not in {"green", "yellow"}:
                        return False, f"Opensearch status is {health_check_response['status']}."
                else:
                    logger.error(f"Failed to Opensearch health check due to missing opensearch config.")
                    return False, f"Failed to Opensearch health check due to missing opensearch config."
        else:
            return None, ""
    except Exception as e:
        logger.error(f"Error in get_opensearch_health_check: {str(e)}")
        if "ConnectionError" in str(e):
            return False, f"Opensearch service is down due to reason:: Failed to connect the opensearch cluster."
        return False, f"Opensearch service is down due to reason:: {str(e)}"
    return True, ""
