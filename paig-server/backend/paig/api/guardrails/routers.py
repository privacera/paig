from fastapi import APIRouter

from api.guardrails.routes.gr_connection_router import gr_connection_router
from api.guardrails.routes.guardrail_router import guardrail_router

paig_guardrails_router = APIRouter()
paig_guardrails_router.include_router(gr_connection_router, prefix="/connection", tags=["Guardrails connections"])
paig_guardrails_router.include_router(guardrail_router, prefix="/guardrail", tags=["Guardrails"])
