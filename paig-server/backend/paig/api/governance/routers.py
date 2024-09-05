from fastapi import APIRouter, Depends

from core.security.authentication import get_auth_user
from api.governance.routes.ai_app_config_download_router import ai_app_config_download_router
from api.governance.routes.ai_app_config_router import ai_app_config_router
from api.governance.routes.ai_app_policy_router import ai_app_policy_router
from api.governance.routes.ai_app_router import ai_app_router
from api.governance.routes.vector_db_policy_router import vector_db_policy_router
from api.governance.routes.vector_db_router import vector_db_router

governance_router = APIRouter(dependencies=[Depends(get_auth_user)])
governance_router.include_router(ai_app_router, prefix="/ai/application", tags=["AI Application Management"])
governance_router.include_router(ai_app_config_router, prefix="/ai/application/{id}", tags=["AI Application Config Management"])
governance_router.include_router(ai_app_config_download_router, prefix="/ai/application/{id}", tags=["AI Application Config Downloader"])
governance_router.include_router(ai_app_policy_router, prefix="/ai/application/{app_id}/policy", tags=["AI Application Policy Management"])
governance_router.include_router(vector_db_router, prefix="/ai/vectordb", tags=["AI Vector DB Management"])
governance_router.include_router(vector_db_policy_router, prefix="/ai/vectordb/{vector_db_id}/policy", tags=["AI Vector DB Policy Management"])