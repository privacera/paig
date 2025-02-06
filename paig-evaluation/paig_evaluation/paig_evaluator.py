import sys
import uuid
from typing import List, Dict

from .promptfoo_utils import (
    suggest_promptfoo_redteam_plugins_with_openai,
    generate_promptfoo_redteam_config,
    run_promptfoo_redteam_evaluation,
    get_all_security_plugins_with_description,
    get_suggested_plugins_with_description,
    check_and_install_npm_dependency
)
from .config import load_config_file


def get_suggested_plugins(purpose: str) -> Dict:
        """
        Get suggested plugins for the application.

        Args:
            purpose (str): Application purpose.

        Returns:
            List[str]: List of suggested plugins.
        """
        suggested_plugins_response = {}
        suggested_plugins = suggest_promptfoo_redteam_plugins_with_openai(purpose)

        if isinstance(suggested_plugins, dict) and "plugins" in suggested_plugins:
            suggested_plugins_response['status'] = 'success'
            suggested_plugins_response['message'] = 'Suggested plugins fetched successfully.'
            suggested_plugins_response['plugins'] = get_suggested_plugins_with_description(suggested_plugins['plugins'])
        else:
            suggested_plugins_response['status'] = 'failed'
            suggested_plugins_response['message'] = str(suggested_plugins)
            suggested_plugins_response['plugins'] = []
        return suggested_plugins_response


def get_all_plugins(plugin_file_path: str = None) -> Dict:
    """
    Get all security plugins.

    Returns:
        Dict: List of all security plugins.
    """
    return get_all_security_plugins_with_description(plugin_file_path)


def init_setup():
    """
    Initialize the setup by checking and installing the npm dependency.
    """
    eval_config = load_config_file()
    if 'npm_dependency' in eval_config:
        if 'promptfoo' in eval_config['npm_dependency']:
            version = eval_config['npm_dependency']['promptfoo']
            check_and_install_npm_dependency('promptfoo', version)
        else:
            sys.exit('No promptfoo dependency found in the configuration file.')
    else:
        sys.exit('No npm dependency found in the configuration file.')


class PAIGEvaluator:

    def init(self):
        """
        Initialize the evaluator.

        Returns:
            dict: Initial configuration.
        """
        initial_config = {
            "paig_eval_id": str(uuid.uuid4())
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

    def evaluate(self, paig_eval_id: str, generated_prompts: dict, base_prompts: dict = None, custom_prompts: dict = None, verbose: bool = False) -> dict:
        """
        Run the evaluation process.

        Args:
            paig_eval_id (str): Evaluation ID.
            generated_prompts (dict): Promptfoo redteam configuration.
            base_prompts (dict): Base prompts.
            custom_prompts (dict): Custom prompts.
            verbose (bool): Verbose mode.

        Returns:
            dict: Evaluation results.
        """

        return run_promptfoo_redteam_evaluation(paig_eval_id, generated_prompts, base_prompts, custom_prompts, verbose)