import asyncio
import json
from typing import List, Optional
from fastapi import APIRouter, Request, Response, Depends, Query, HTTPException

from api.evaluation.api_schemas.eval_config_schema import ConfigCreateRequest
from core.controllers.paginated_response import Pageable
from api.evaluation.api_schemas.eval_schema import EvaluationCommonModel, EvaluationConfigPlugins, IncludeQueryParams,\
include_query_params, exclude_query_params, QueryParamsBase
from core.utils import SingletonDepends
from core.security.authentication import get_auth_user
from api.evaluation.controllers.eval_controllers import EvaluationController
evaluation_router = APIRouter()

evaluator_controller_instance = Depends(SingletonDepends(EvaluationController, called_inside_fastapi_depends=True))


@evaluation_router.post("/save_and_run")
async def evaluation_save_and_run(
    body_params: ConfigCreateRequest,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user)
):
    return await evaluation_controller.create_and_run_evaluation(body_params.model_dump(), user)


@evaluation_router.post("/{config_id}/run")
async def evaluation_run(
    config_id: int,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
    try:
        return await evaluation_controller.run_evaluation(config_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@evaluation_router.get("/search")
async def get_evaluation_results(
        request: Request,
        response: Response,
        user: dict = Depends(get_auth_user),
        page: int = Query(0, description="The page number to retrieve"),
        size: int = Query(10, description="The number of items per page"),
        sort: List[str] = Query([], description="The sort options"),
        fromTime: Optional[int] = Query(None, description="The from time"),
        toTime: Optional[int] = Query(None, description="The to time"),
        includeQuery: IncludeQueryParams = Depends(include_query_params),
        excludeQuery: QueryParamsBase = Depends(exclude_query_params),
        evaluation_controller: EvaluationController = evaluator_controller_instance,
):
    return await evaluation_controller.get_evaluation_results(includeQuery, excludeQuery, page, size, sort,
                                                                       fromTime, toTime)





@evaluation_router.post("/{eval_id}/rerun")
async def evaluation_rerun(
    eval_id: int,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
    # return await evaluation_controller.run_evaluation(evaluation_config)
    try:
        return await evaluation_controller.rerun_evaluation(eval_id, user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@evaluation_router.delete("/report/{eval_id}")
async def evaluation_delete(
    eval_id: int,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
    user: dict = Depends(get_auth_user),
):
    # return await evaluation_controller.run_evaluation(evaluation_config)
    try:
        return await evaluation_controller.delete_evaluation(eval_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))