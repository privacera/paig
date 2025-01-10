from fastapi import APIRouter

from api.evaluation.routes.evaluation_router import evaluation_router

evaluation_router_paths = APIRouter()
evaluation_router_paths.include_router(evaluation_router, prefix="/api", tags=["Evaluation_routers"])