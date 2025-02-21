import sys
import uuid
from typing import List, Dict

from .promptfoo_utils import (
    suggest_promptfoo_redteam_plugins_with_openai,
    generate_promptfoo_redteam_config,
    run_promptfoo_redteam_evaluation,
    get_all_security_plugins_with_description,
    get_suggested_plugins_with_description,
    check_and_install_npm_dependency,
    get_response_object,
    validate_generate_prompts_request_params,
    validate_evaluate_request_params
)
from .config import load_config_file

eval_config = load_config_file()


def get_suggested_plugins(purpose: str) -> Dict:
        """
        Get suggested plugins for the application.

        Args:
            purpose (str): Application purpose.

        Returns:
            List[str]: List of suggested plugins.
        """
        response = get_response_object()
        response['result'] = []
        try:
            suggested_plugins = suggest_promptfoo_redteam_plugins_with_openai(purpose)
            if isinstance(suggested_plugins, dict) and "plugins" in suggested_plugins:
                if isinstance(suggested_plugins['plugins'], list):
                    response['result'] = get_suggested_plugins_with_description(suggested_plugins['plugins'])
                    response['status'] = 'success'
                    response['message'] = 'Suggested plugins fetched successfully'
                else:
                    response['message'] = 'Invalid response received from the OpenAI API for suggested plugins'
            else:
                response['message'] = str(suggested_plugins)
        except Exception as e:
            response['message'] = str(e)
        finally:
            return response



def get_all_plugins(plugin_file_path: str = None) -> Dict:
    """
    Get all security plugins.

    Returns:
        Dict: List of all security plugins.
    """
    response = get_response_object()
    response['result'] = []
    try:
        all_plugins = get_all_security_plugins_with_description(plugin_file_path)
        if isinstance(all_plugins, list):
            response['result'] = all_plugins
            response['status'] = 'success'
            response['message'] = 'All plugins fetched successfully'
        else:
            response['message'] = str(all_plugins)
    except Exception as e:
        response['message'] = str(e)
    finally:
        return response


def init_setup():
    """
    Initialize the setup by checking and installing the npm dependency.
    """
    response = get_response_object()
    try:
        if 'npm_dependency' in eval_config:
            if 'promptfoo' in eval_config['npm_dependency']:
                version = eval_config['npm_dependency']['promptfoo']
                check_and_install_npm_dependency('promptfoo', version)
                response["status"] = 'success'
                response["message"] = 'Setup initialized successfully'
            else:
                response["message"] = 'No promptfoo dependency found in the configuration file'
        else:
            response["message"] = 'No npm dependency found in the configuration file'
    except Exception as e:
        response["message"] = f'Error occurred while initializing the setup: {e}'
    finally:
        return response

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
        response = get_response_object()
        response['result'] = {}
        try:
            is_validated, message = validate_generate_prompts_request_params(application_config, plugins, targets)
            response['message'] = message
            if is_validated:
                generated_prompts = generate_promptfoo_redteam_config(application_config, plugins, targets, verbose=verbose)
                if generated_prompts:
                    response['result'] = generated_prompts
                    response['status'] = 'success'
                    response['message'] = 'Prompts generated successfully'
                else:
                    response['message'] = 'Failed to generate prompts'
        except Exception as e:
            response['message'] = str(e)
        finally:
            return response

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
        response = get_response_object()
        response['result'] = {}
        try:
            is_validated, message = validate_evaluate_request_params(paig_eval_id, generated_prompts, base_prompts, custom_prompts)
            response['message'] = message
            if is_validated:
                eval_result = run_promptfoo_redteam_evaluation(paig_eval_id, generated_prompts, base_prompts, custom_prompts, verbose)
                if eval_result:
                    response['result'] = eval_result
                    response['status'] = 'success'
                    response['message'] = 'Evaluation completed successfully'
                else:
                    response['message'] = 'Failed to run the evaluation'
        except Exception as e:
            response['message'] = str(e)
        finally:
            return response