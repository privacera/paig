from fastapi import APIRouter
from api.shield.routes.init_app_router import init_app_router
from api.shield.routes.authorize_app_router import authorize_app_router
from api.shield.routes.authorize_vectordb_router import authorize_vectordb_router
from api.shield.routes.audit_app_router import audit_app_router

shield_router = APIRouter()

shield_router.include_router(init_app_router, prefix="/init")
shield_router.include_router(authorize_app_router, prefix="/authorize")
shield_router.include_router(authorize_vectordb_router, prefix="/authorize/vectordb")
shield_router.include_router(audit_app_router, prefix="/audit")
