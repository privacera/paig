from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from api.guardrails.routers import paig_guardrails_router
from api.user.routers import user_router
from api.authz.routers import authz_router
from api.encryption.routers import encryption_router
from api.governance.routers import governance_router
from api.governance.routes.metadata_value_router import metadata_value_router
from api.governance.routes.metadata_key_router import metadata_key_router
from api.governance.routes.tag_router import tag_router
from api.audit.routers import data_service_router
from api.shield.routers import shield_router
from api.eval.routers import evaluation_router_paths
from api.apikey.routers import api_key_router
from core.security.authentication import get_auth_user
from api.governance.routes.ai_app_config_download_router import ai_app_config_download_with_key_router
from utils1.custom_metrics import users_total_gauge
from api.user.services.user_service import UserService
from utils1.custom_metrics import groups_total_gauge
from api.user.services.group_service import GroupService
from core.utils import SingletonDepends

router = APIRouter()

router.include_router(governance_router, prefix="/governance-service/api")
router.include_router(tag_router, prefix="/account-service/api/tags", tags=["Tag Attributes"])
router.include_router(metadata_value_router, prefix="/account-service/api/vectordb/metadata/value", tags=["Vector DB Metadata values"])
router.include_router(metadata_key_router, prefix="/account-service/api/vectordb/metadata/key", tags=["Vector DB Metadata keys"])
router.include_router(encryption_router, prefix="/account-service/api/data-protect", tags=["Encryption Keys"])
router.include_router(user_router, prefix="/account-service", tags=["User"])
router.include_router(authz_router, prefix="/authz-service/api", tags=["Authorization"])
router.include_router(data_service_router, prefix="/data-service", tags=["Data Service"])
router.include_router(shield_router, prefix="/shield", tags=["Shield"])
router.include_router(evaluation_router_paths, prefix="/eval-service", tags=["Evaluation"], dependencies=[Depends(get_auth_user)])
router.include_router(paig_guardrails_router, prefix="/guardrail-service/api", dependencies=[Depends(get_auth_user)])
router.include_router(api_key_router, prefix="/account-service/api/apikey", tags=["API Key"])
router.include_router(ai_app_config_download_with_key_router, prefix="/api/ai/application/config", tags=["Governance with API Key"])

@router.get("/metrics")
async def metrics(
    user_service: UserService = Depends(SingletonDepends(UserService, called_inside_fastapi_depends=True)),
    group_service: GroupService = Depends(SingletonDepends(GroupService, called_inside_fastapi_depends=True)),
):
    """ Prometheus metrics endpoint """
    try:
        # user count
        try:
            user_count = await user_service.get_user_count()
            users_total_gauge.set(user_count)
        except Exception:
            pass
        # groups count
        try:
            group_count = await group_service.get_group_count()
            groups_total_gauge.set(group_count)
        except Exception:
            pass

        # return all metrics
        return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        # helpful error message for debugging
        return PlainTextResponse(f"Metrics endpoint failed: {e}", status_code=500)
__all__ = ["router"]
