from fastapi import APIRouter, Depends

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
from core.security.authentication import get_auth_user

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
router.include_router(paig_guardrails_router, prefix="/guardrail-service/api", dependencies=[Depends(get_auth_user)])

__all__ = ["router"]
