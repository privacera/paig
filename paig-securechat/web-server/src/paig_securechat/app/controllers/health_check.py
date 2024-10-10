from services.health_check import get_db_health_check, get_opensearch_health_check
from datetime import datetime
import logging
from core import config
from _version import __version__
logger = logging.getLogger(__name__)


APP_NAME = "SecureChat"
HEALTHY = "Healthy"
UNHEALTHY = "Unhealthy"
REASON = "Reason"
SERVICE = "Service"
STATUS = "Status"
DETAILS = "Details"


class HealthController:
    def __init__(self, db_session):
        self.session = db_session
        self.config = config.Config

    def get_reason(self, reason):
        return f", {reason}" if reason else ""


    async def get_health_check(self) -> dict:
        db_status, db_reason = await get_db_health_check(self.session)
        opensearch_status, opensearch_reason = await get_opensearch_health_check(self.config)
        health_dict = dict()
        health_dict['Server'] = APP_NAME
        health_dict['Time'] = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        health_dict['Version'] = __version__
        health_dict[DETAILS] = list()
        health_dict[REASON] = ""
        health_dict[STATUS] = HEALTHY
        health_dict[DETAILS].append(dict({SERVICE: "Database", STATUS: HEALTHY if db_status else UNHEALTHY,
                                          REASON: db_reason}))
        health_dict[REASON] += db_reason
        if not db_status:
            health_dict[STATUS] = UNHEALTHY
        if opensearch_status is not None:
            health_dict[DETAILS].append(dict({SERVICE: "OpenSearch", STATUS: HEALTHY if opensearch_status else UNHEALTHY,
                                              REASON: opensearch_reason}))
            health_dict[REASON] += opensearch_reason if health_dict[REASON] == "" else self.get_reason(opensearch_reason)
            if not opensearch_status:
                health_dict[STATUS] = UNHEALTHY

        return health_dict
