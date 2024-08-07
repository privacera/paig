from fastapi import APIRouter

from api.authz.routes.paig_authorizer_router import paig_authorizer_router

authz_router = APIRouter()
authz_router.include_router(paig_authorizer_router, prefix="/authz", tags=["Authorization"])
