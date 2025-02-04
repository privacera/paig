import uuid
from typing import List, Dict
import sys

from .promptfoo_utils import (
    suggest_promptfoo_redteam_plugins_with_openai,
    generate_promptfoo_redteam_config,
    run_promptfoo_redteam_evaluation,
    get_all_security_plugins,
    get_plugins_response,
    check_command_exists,
    check_npm_dependency,
    install_npm_dependency
)


def get_suggested_plugins(purpose: str) -> Dict:
        """
        Get suggested plugins for the application.

        Args:
            purpose (str): Application purpose.

        Returns:
            List[str]: List of suggested plugins.
        """
        suggested_plugins = suggest_promptfoo_redteam_plugins_with_openai(purpose)
        return get_plugins_response(suggested_plugins)


def get_all_plugins(plugin_file_path: str = None) -> Dict:
    """
    Get all security plugins.

    Returns:
        Dict: List of all security plugins.
    """
    return get_all_security_plugins(plugin_file_path)


def init_setup():
    """
    Initialize the setup by checking and installing the npm dependency.
    """
    if not check_command_exists("node"):
        sys.exit("Node.js is not installed. Please install it first.")

    if not check_command_exists("npm"):
        sys.exit("npm is not installed. Please install Node.js, which includes npm.")

    package_name = "promptfoo"
    version = "0.102.4"

    if check_npm_dependency(package_name, version):
        print(f"Dependent npm package is already installed.")
    else:
        print(f"Dependent npm package, Installing now...")
        install_npm_dependency(package_name, version)



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


    def generate_prompts(self, application_config: dict, plugins: List[str], targets: List[Dict], verbose: bool = False) -> dict:
        """
        Generate prompts for the application.

        Args:
            application_config (dict): Application configuration.
            plugins (List[str]): List of plugins.
            targets (List[Dict]): List of targets.
            verbose (bool): Verbose mode.

        Returns:
            dict: Generated prompts.
        """
        return generate_promptfoo_redteam_config(application_config, plugins, targets, verbose=verbose)

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