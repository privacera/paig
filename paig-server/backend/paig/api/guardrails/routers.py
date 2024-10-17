from fastapi import APIRouter, Depends

from api.guardrails.routes.guardrail_router import guardrail_router
from api.guardrails.routes.gr_connection_router import gr_connection_router
from core.security.authentication import get_auth_user

paig_guardrails_router = APIRouter(dependencies=[Depends(get_auth_user)])
paig_guardrails_router.include_router(gr_connection_router, prefix="/connection", tags=["Guardrails connections"])
paig_guardrails_router.include_router(guardrail_router, prefix="/guardrail", tags=["Guardrails"])
