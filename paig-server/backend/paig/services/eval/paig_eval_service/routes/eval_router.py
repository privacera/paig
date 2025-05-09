from fastapi import APIRouter, Depends, HTTPException
from ..api_schemas.eval_schema import GetCategories, SaveAndRunRequest, RunRequest
from core.utils import SingletonDepends
from core.middlewares.request_session_context_middleware import get_user
from ..controllers.eval_controllers import EvaluationController
evaluation_router = APIRouter()

evaluator_controller_instance = Depends(SingletonDepends(EvaluationController, called_inside_fastapi_depends=True))


@evaluation_router.post("/save_and_run")
async def evaluation_save_and_run(
    body_params: SaveAndRunRequest,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
):
    user: dict = get_user()
    return await evaluation_controller.create_and_run_evaluation(body_params.model_dump(), user['username'])


@evaluation_router.post("/{config_id}/run")
async def evaluation_run(
    config_id: int,
    body_params: RunRequest,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
):
    user: dict = get_user()
    return await evaluation_controller.run_evaluation(config_id, user['username'], body_params.report_name, body_params.auth_user)

@evaluation_router.post("/{eval_id}/rerun")
async def evaluation_rerun(
    eval_id: str,
    body_params: RunRequest,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
):
    user: dict = get_user()
    return await evaluation_controller.rerun_evaluation(eval_id, user, body_params.report_name)


@evaluation_router.post("/categories")
async def get_categories(
    body_params: GetCategories,
    evaluation_controller: EvaluationController = evaluator_controller_instance,
):
    purpose = body_params.purpose
    return await evaluation_controller.get_categories(purpose)

