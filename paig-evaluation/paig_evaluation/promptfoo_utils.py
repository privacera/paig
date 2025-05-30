import json
import os
from typing import List, Dict

import openai
import yaml
import sys
import uuid
import logging

from .command_utils import run_command_in_background, wait_for_process_complete
from .file_utils import write_yaml_file, read_yaml_file, read_json_file
import subprocess
from typing import Union
from . import constants


logger = logging.getLogger("paig_eval")


def ensure_promptfoo_config(email: str):
    """
    Ensures that the ~/.promptfoo/promptfoo.yaml file exists with the specified email.

    Args:
        email (str): The email address to store in the configuration.
    """
    # Define the file path
    home_directory = os.path.expanduser("~")
    config_directory = os.path.join(home_directory, ".promptfoo")
    config_file_path = os.path.join(config_directory, "promptfoo.yaml")

    # Define the content to write
    content = {
        "account": {
            "email": email
        }
    }

    # Ensure the directory exists
    os.makedirs(config_directory, exist_ok=True)

    # Create the file with the content if it doesn't exist
    if not os.path.exists(config_file_path):
        with open(config_file_path, "w") as file:
            yaml.dump(content, file, default_flow_style=False)
    else:
        # Update the email address if the file exists
        with open(config_file_path, "r") as file:
            existing_content = yaml.safe_load(file)
            if "account" not in existing_content:
                existing_content["account"] = {}
            if "email" not in existing_content["account"]:
                existing_content["account"]["email"] = email

        with open(config_file_path, "w") as file:
            yaml.dump(existing_content, file, default_flow_style=False)

def get_response_object() -> Dict:
    """
    Returns a response object with default values.

    Returns:
        Dict: The response object.
    """
    return {
        "status": "failed",
        "message": "",
        "result": None
    }


def check_package_exists(package_name: str) -> bool:
    """
    Check if a command exists in the system.

    Args:
        command (str): The command to check.

    Returns:
        bool: True if the command exists, False otherwise.
    """
    try:
        subprocess.run([package_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        logger.error(f"{package_name} is not installed.")
        return False


def check_npm_dependency(package_name: str, version: str) -> bool:
    """
    Check if an npm package with a specific version is globally installed.

    Args:
        package_name (str): The name of the package to check.
        version (str): The version of the package to check.

    Returns:
        bool: True if the package and version are installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["npm", "list", "-g", f"{package_name}@{version}", "--depth", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return f"{package_name}@{version}" in result.stdout
    except FileNotFoundError:
        logger.error("npm is not installed.")
        sys.exit("npm is not installed. Please install Node.js first.")


def install_npm_dependency(package_name: str, version: str) -> None:
    """
    Install an npm package globally.

    Args:
        package_name (str): The name of the package to install.
        version (str): The version of the package to install.
    """
    try:
        command = f"npm install -g {package_name}@{version}"
        process = run_command_in_background(command)
        wait_for_process_complete(process, verbose=True)
        if process.returncode == 0:
            logger.info("Successfully installed npm package.")
        else:
            sys.exit("Failed to install npm package.")
    except Exception as e:
        logger.error(f"Error installing npm package: {e}")
        raise RuntimeError(f"Error installing npm package: {e}")


def check_and_install_npm_dependency(package_name, version):
    """
    Check and install the npm dependency if it is not already installed.
    """
    if not check_package_exists("node"):
        logger.error("Node.js is not installed.")
        raise RuntimeError("Node.js is not installed. Please install it first.")

    if not check_package_exists("npm"):
        logger.error("npm is not installed.")
        raise RuntimeError("npm is not installed. Please install Node.js, which includes npm.")

    if check_npm_dependency(package_name, version):
        logger.info(f"Dependent npm package is already installed.")
    else:
        logger.info(f"Installing npm package...")
        install_npm_dependency(package_name, version)


def get_suggested_plugins_with_info(plugins) -> List:
    """
    Get suggested plugins with description.

    Args:
        plugins (List[Dict]): List of plugins.

    Returns:
        List: List of suggested plugins with description.
    """
    suggested_security_plugins = []
    security_plugins = read_and_get_security_plugins()
    if isinstance(security_plugins, str):
        return suggested_security_plugins
    for plugin in plugins:
        if plugin in security_plugins:
            plugin_info = security_plugins[plugin]
            suggested_security_plugins.append(
                {
                    "Name": plugin,
                    "Description":plugin_info['description'],
                    "Severity": plugin_info['severity'],
                    "Type": plugin_info['type']
                }
            )

    return suggested_security_plugins


def get_all_security_plugins_with_info() -> List[Dict]:
    """
    Returns a list of all available security plugins with descriptions.

    Returns:
        List[Dict]:  A list of dictionaries containing the plugin name and description.
    """

    security_plugins = read_and_get_security_plugins()
    security_plugins_with_description = []
    if isinstance(security_plugins, str):
        return security_plugins
    for plugin_name, plugin_info in security_plugins.items():
        security_plugins_with_description.append(
            {
                "Name": plugin_name,
                "Description": plugin_info['description'],
                "Severity": plugin_info['severity'],
                "Type": plugin_info['type']
            }
        )
    return security_plugins_with_description

def get_security_plugin_map() -> Dict:
    """
    Returns a dictionary of all available security plugins with descriptions.

    Returns:
        Dict: A dictionary containing the plugin name and description.
    """

    return read_and_get_security_plugins()



def read_and_get_security_plugins() -> Union[str, Dict]:
    """
    Reads the security plugins from the specified file and returns a list of available plugins.

    Returns:
        Union[str, Dict]: Error message if the file is not found or a dict of security plugins
    """
    # check if already set
    if constants.SECURITY_PLUGINS:
        return constants.SECURITY_PLUGINS

    # Check if file exists
    if constants.PLUGIN_FILE_PATH and not os.path.exists(constants.PLUGIN_FILE_PATH):
        return f"Error: Custom Security plugins file not found, file_path={constants.PLUGIN_FILE_PATH}"

    # Check if default file exist
    if constants.DEFAULT_PLUGIN_FILE_PATH and not os.path.exists(constants.DEFAULT_PLUGIN_FILE_PATH):
        return f"Error: Default Security plugins file not found, file_path={constants.DEFAULT_PLUGIN_FILE_PATH}"

    # Read JSON content
    security_plugins = read_json_file(constants.DEFAULT_PLUGIN_FILE_PATH)

    # Handle invalid JSON response
    if not isinstance(security_plugins, dict):
        return "Error: Invalid security plugins data."

    if constants.PLUGIN_FILE_PATH:
        custom_security_plugins = read_json_file(constants.PLUGIN_FILE_PATH)
        # Handle invalid JSON response
        if not isinstance(custom_security_plugins, dict):
            return "Error: Invalid custom security plugins data."
        security_plugins.update(custom_security_plugins)

    PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION = os.getenv('PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION')

    filtered_security_plugins = dict()
    for plugin in security_plugins:
        if not security_plugins[plugin].get("enabled", True):
            continue
        if PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION in {'1', 'true', 'True'} and security_plugins[plugin].get("remote", False):
            continue
        filtered_security_plugins[plugin] = security_plugins[plugin]


    return filtered_security_plugins


def validate_generate_prompts_request_params(application_config, plugins, targets):
    """
    Validate the request parameters for generating prompts.

    Args:
        application_config (dict): Application configuration.
        plugins (List[str]): List of plugins.
        targets (List[Dict]): List of targets.

    Returns:
        bool: True if the parameters are valid, False otherwise.
    """
    if not application_config or not isinstance(application_config, dict) or "paig_eval_id" not in application_config or "purpose" not in application_config:
        logger.error("Invalid application configuration, required as dictionary with 'paig_eval_id' and 'purpose'")
        return False, "Invalid application configuration, required as dictionary with 'paig_eval_id' and 'purpose'"

    if not plugins or not isinstance(plugins, list):
        logger.error("Invalid plugins, required valid list of strings")
        return False, "Invalid plugins, required valid list of strings"

    if not targets or not isinstance(targets, list) or not all(isinstance(target, dict) for target in targets):
        logger.error("Invalid targets, required valid list of dictionary objects")
        return False, "Invalid targets, required valid list of dictionary objects"
    return True, ""


def is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False


def validate_evaluate_request_params(paig_eval_id, generated_prompts, base_prompts: dict = None, custom_prompts: dict = None):
    """
    Validate the request parameters for evaluating prompts.

    Args:
        paig_eval_id (str): Evaluation ID.
        generated_prompts (dict): Generated prompts.
        base_prompts (dict): Base prompts.
        custom_prompts (dict): Custom prompts.

    Returns:
        bool: True if the parameters are valid, False otherwise.
    """
    if not paig_eval_id or not isinstance(paig_eval_id, str) or not is_valid_uuid(paig_eval_id):
        logger.error("Invalid evaluation ID, required as a valid UUID")
        return False, "Invalid evaluation ID, required as a valid UUID"

    if not generated_prompts or not isinstance(generated_prompts, dict):
        logger.error("Invalid generated prompts, required valid dictionary")
        return False, "Invalid generated prompts, required valid dictionary"

    if base_prompts and not isinstance(base_prompts, dict):
        logger.error("Invalid base prompts, required valid dictionary")
        return False, "Invalid base prompts, required valid dictionary"

    if custom_prompts and not isinstance(custom_prompts, dict):
        logger.error("Invalid custom prompts, required valid dictionary")
        return False, "Invalid custom prompts, required valid dictionary"

    return True, ""


def suggest_promptfoo_redteam_plugins_with_openai(purpose: str, model: str = "gpt-4") -> Dict | str:
    """
    Suggests plugins to test security vulnerabilities based on the purpose of the application using OpenAI.

    Args:
        purpose (str): The purpose of the application.
        model (str): The OpenAI model to use. Default is "gpt-4".

    Returns:
        List[Dict[str, str]] | str: The list of suggested plugins with descriptions or an error message.
    """
    security_plugins = read_and_get_security_plugins()
    if isinstance(security_plugins, str):
        return security_plugins

    plugins_names_list = list(security_plugins.keys())

    plugins_json = json.dumps({"plugins": plugins_names_list}, indent=2)

    prompt = f"""
        You are an AI security expert specializing in identifying vulnerabilities in large language model applications. The user will provide the purpose of their application, and your task is to suggest plugins to test security vulnerabilities based on purpose.

        Below is the list of supported plugins:
        {plugins_json}

        Provide the output in the below JSON format:
        {{
          "plugins": [
            "pii",
            "pii:api-db",
            ....
          ]
        }}

        Don't use code snippets or any programming language specific syntax. Just provide the output in plain text format.

        Application purpose is: {purpose}
        """

    try:
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an AI security expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0,
            functions = [
                {
                    "name": "suggest_plugins",
                    "description": "Suggests security plugins based on the application's purpose.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "plugins": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of suggested plugins for the application."
                            }
                        },
                        "required": ["plugins"]
                    }
                }
            ],
            function_call = {"name": "suggest_plugins"}  # Explicitly call the function
        )
        try:
            return json.loads(response.choices[0].message.function_call.arguments)
        except Exception as e:
            return f"Error: {e}"
    except openai.OpenAIError as e:
        return f"Error: {e}"


def generate_promptfoo_redteam_config(application_config: dict, plugins: List[str], targets: List[Dict], verbose: bool = False) -> dict:
    """
    Generate the promptfoo redteam configuration file based on the application configuration.

    Args:
        application_config (dict): Application configuration.
        plugins (List[str]): List of plugins.
        targets (List[Dict]): List of targets.
        verbose (bool): Verbose mode.

    Returns:
        dict: Promptfoo redteam configuration.
    """
    generated_config = None
    promptfoo_config_file_name = None
    output_file_name = None
    try:
        paig_evaluation_app_id = application_config.get("paig_eval_id")
        application_name = application_config.get("name", "PAIG Evaluation Application")
        description = application_config.get("description", "PAIG Evaluation Application")
        purpose = application_config.get("purpose")

        # Create promptfoo redteam config file
        readteam_config = {
            "description": description,
            "targets": targets,
            "redteam": {
                "numTests": 5,
                "language": "English",
                "purpose": purpose,
                "plugins": plugins
            }
        }

        promptfoo_config_file_name = f"tmp_{paig_evaluation_app_id}_promptfoo_redteam_config.yaml"
        output_file_name = f"tmp_{paig_evaluation_app_id}_promptfoo_generated_prompts.yaml"
        write_yaml_file(promptfoo_config_file_name, readteam_config)

        # Generate prompts for redteam
        command = f"promptfoo redteam generate --max-concurrency 5 --config {promptfoo_config_file_name} --output {output_file_name}"

        process = run_command_in_background(command)
        wait_for_process_complete(process, verbose=verbose)

        if not os.path.exists(output_file_name):
            error_message = f"Prompts generation failed for given config with ID {paig_evaluation_app_id}."
            raise RuntimeError(error_message)
        # Read generated prompts
        generated_config = read_yaml_file(output_file_name)
    except Exception as e:
        logger.error(f"Error while generating prompts: {e}")
    finally:
        if promptfoo_config_file_name and os.path.exists(promptfoo_config_file_name):
            os.remove(promptfoo_config_file_name)
        if output_file_name and os.path.exists(output_file_name):
            os.remove(output_file_name)
        return generated_config


def run_promptfoo_redteam_evaluation(paig_eval_id: str, promptfoo_redteam_config: dict, base_prompts: dict = None, custom_prompts: dict = None, verbose: bool = False) -> dict:
    """
    Run the promptfoo redteam evaluation process.

    Args:
        paig_eval_id (str): Evaluation ID.
        promptfoo_redteam_config (dict): Promptfoo redteam configuration.
        base_prompts (dict): Base prompts.
        custom_prompts (dict): Custom prompts.
        verbose (bool): Verbose mode.

    Returns:
        dict: Evaluation report.
    """

    # Create updated promptfoo redteam configuration
    evaluation_report = None
    promptfoo_generated_prompts_file_name = f"tmp_{paig_eval_id}_promptfoo_generated_prompts.yaml"
    output_file_name = f"tmp_{paig_eval_id}_promptfoo_evaluation_report.json"
    try:
        base_tests = base_prompts.get("tests") if base_prompts else []
        custom_tests = custom_prompts.get("tests") if custom_prompts else []
        promptfoo_redteam_config["tests"] = base_tests + custom_tests + promptfoo_redteam_config["tests"]

        write_yaml_file(promptfoo_generated_prompts_file_name, promptfoo_redteam_config)

        # Run promptfoo redteam evaluation
        command = f"promptfoo redteam eval --no-cache --config {promptfoo_generated_prompts_file_name} --output {output_file_name}"

        process = run_command_in_background(command)
        wait_for_process_complete(process, verbose=verbose)

        if not os.path.exists(output_file_name):
            error_message = f"Evaluation failed for given config with ID {paig_eval_id}."
            raise RuntimeError(error_message)

        # Read evaluation report
        evaluation_report = read_json_file(output_file_name)
    except Exception as e:
        logger.error(f"Error while running evaluation process: {e}")
    finally:
        if os.path.exists(promptfoo_generated_prompts_file_name):
            os.remove(promptfoo_generated_prompts_file_name)
        if os.path.exists(output_file_name):
            os.remove(output_file_name)
        return evaluation_report

