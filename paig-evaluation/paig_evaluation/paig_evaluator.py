import uuid
from typing import List, Dict

from .promptfoo_utils import suggest_promptfoo_redteam_plugins_with_openai, \
    generate_promptfoo_redteam_config, run_promptfoo_redteam_evaluation


class PAIGEvaluator:

    def init(self):
        """
        Initialize the evaluator.

        Returns:
            dict: Initial configuration.
        """
        eval_id = str(uuid.uuid4())

        initial_config = {
            "paig_eval_id": eval_id
        }

        return initial_config

    def get_suggested_plugins(self, purpose: str) -> Dict:
        """
        Get suggested plugins for the application.

        Args:
            purpose (str): Application purpose.

        Returns:
            List[str]: List of suggested plugins.
        """
        return suggest_promptfoo_redteam_plugins_with_openai(purpose)

    def generate_prompts(self, application_config: dict, plugins: List[str], verbose: bool = False) -> dict:
        """
        Generate prompts for the application.

        Args:
            application_config (dict): Application configuration.
            plugins (List[str]): List of plugins.
            verbose (bool): Verbose mode.

        Returns:
            dict: Generated prompts.
        """
        return generate_promptfoo_redteam_config(application_config, plugins, verbose=verbose)

    def evaluate(self, eval_id: str, generated_prompts: dict, base_prompts: dict = None, custom_prompts: dict = None, verbose: bool = False) -> dict:
        """
        Run the evaluation process.

        Args:
            eval_id (str): Evaluation ID.
            generated_prompts (dict): Promptfoo redteam configuration.
            base_prompts (dict): Base prompts.
            custom_prompts (dict): Custom prompts.
            verbose (bool): Verbose mode.

        Returns:
            dict: Evaluation results.
        """

        return run_promptfoo_redteam_evaluation(eval_id, generated_prompts, base_prompts, custom_prompts, verbose)