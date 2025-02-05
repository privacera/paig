from fastapi import APIRouter

from api.evaluation.routes.eval_router import evaluation_router

from api.evaluation.routes.eval_target_router import evaluation_target_router
from api.evaluation.routes.eval_config_router import evaluation_config_router

evaluation_router_paths = APIRouter()

evaluation_router_paths.include_router(evaluation_router, prefix="/api/eval", tags=["Evaluation Run"])
evaluation_router_paths.include_router(evaluation_target_router, prefix="/api/target", tags=["Evaluation Target"])
evaluation_router_paths.include_router(evaluation_config_router, prefix="/api/config", tags=["Evaluation Config"])