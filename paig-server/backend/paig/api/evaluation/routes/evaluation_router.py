import json
from typing import List
from fastapi import APIRouter, Depends, status, Query
from core.controllers.paginated_response import Pageable
from api.evaluation.api_schemas.evluation_schema import EvaluationCommonModel, EvaluationConfigPlugins
from core.utils import SingletonDepends
from paig_evaluation.paig_eval import PaigEval
import os
evaluation_router = APIRouter()

eval_obj = PaigEval(output_directory="new_workdir")
if not os.path.exists("new_workdir"):
    os.mkdir("new_workdir")

@evaluation_router.post("/init")
async def evaluation_init(
    application_config: EvaluationCommonModel,
):
    """
    Setuo evaluations
    """
    try:
        application_config = application_config.dict()
        config_plugins = eval_obj.init_setup(application_config=json.dumps(application_config))
        config_plugins = json.loads(config_plugins)
        if config_plugins is None:
            return {"error": "Evaluation setup failed.Please check if promptfoo is installed and running."}
        return config_plugins
    except Exception as e:
        return {"error": str(e)}


@evaluation_router.post("/generate")
async def evaluation_init(
    evaluation_config: EvaluationConfigPlugins,
):
    """
    Setuo evaluations
    """
    eval_obj = PaigEval(output_directory="new_workdir")
    config_plugins = evaluation_config.dict()
    config_plugins.pop("static_prompts", None)
    generated_prompts_config = eval_obj.generate_prompts(config_with_plugins=config_plugins)
    eval_obj.update_generated_prompts_config(generated_prompts_config)

    user_prompts_list = evaluation_config.static_prompts
    #prepare object
    if user_prompts_list:
        for prompt in user_prompts_list:
            prompt_obj = {"vars": {"prompt": prompt['prompt']}, "assert": [
                {"type": "llm-rubric", "value": prompt['criteria']}
            ]}
            user_prompts_list.append(prompt_obj)

    eval_obj.append_user_prompts(user_prompts_list=user_prompts_list)
    report = eval_obj.run(verbose=False)
    return report
