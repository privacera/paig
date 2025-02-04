import json
import os
from typing import List, Dict

import openai
import yaml
import sys

from .command_utils import run_command_in_background, wait_for_process_complete
from .file_utils import write_yaml_file, read_yaml_file, read_json_file
import subprocess


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


def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in the system.

    Args:
        command (str): The command to check.

    Returns:
        bool: True if the command exists, False otherwise.
    """
    try:
        subprocess.run([command, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
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
            print("Successfully installed npm package.")
        else:
            sys.exit("Failed to install npm package.")
    except Exception as e:
        sys.exit(f"Error installing npm package: {e}")


def get_suggested_plugins_with_description(plugins) -> List:
    """
    Get suggested plugins with description.

    Args:
        plugins (List[Dict]): List of plugins.

    Returns:
        List: List of suggested plugins with description.
    """
    suggested_security_plugins = []
    security_plugins = get_all_security_plugins()
    for plugin in plugins:
        suggested_security_plugins.append(
            {
                "Name": plugin,
                "Description": security_plugins[plugin]
            }
        )

    return suggested_security_plugins


def get_plugins_response(plugins) -> Dict:
    """
    Plugins response.

    Args:
        plugins (List[str]): List of plugins.
        status (str): Status.

    Returns:
        Dict: Plugins response.
    """
    suggested_plugins_response = {}
    if isinstance(plugins, dict) and "plugins" in plugins:
        suggested_plugins_response['plugins'] = get_suggested_plugins_with_description(plugins['plugins'])
        suggested_plugins_response['status'] = 'success'
    else:
        suggested_plugins_response['status'] = 'failed'
        suggested_plugins_response['message'] = str(plugins)
        suggested_plugins_response['plugins'] = []
    return suggested_plugins_response


def read_security_plugins(plugin_file_path: str = None) -> Dict:
    """
    Reads the security plugins from the specified file.

    Args:
        plugin_file_path (str): The path to the security plugins file.

    Returns:
        Dict: The security plugins.
    """
    if not plugin_file_path:
        plugin_file_path = os.path.join(os.path.dirname(__file__), "conf/security_plugins.json")
    if not os.path.exists(plugin_file_path):
        return f"Error: Security plugins file not found, file_path={plugin_file_path}"
    return read_json_file(plugin_file_path)



def get_all_security_plugins(plugin_file_path: str = None) -> List[Dict]:
    """
    Returns a list of all available security plugins.

    Returns:
        List[Dict]:  A list of dictionaries containing the plugin name and description.
    """

    security_plugins = read_security_plugins(plugin_file_path)
    if isinstance(security_plugins, str):
        return security_plugins

    return get_security_plugins_list(security_plugins)


def get_security_plugins_list(security_plugins_dict):
    """
    Get the security plugins from the list of security plugins.

    Args:
        security_plugins_list (List[Dict]): List of security plugins.

    Returns:
        List[Dict]: List of security plugins.
    """
    all_plugins_dict = security_plugins_dict['local_plugins']
    if os.getenv('PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION') not in {'1', 'true', 'True'}:
        all_plugins_dict.update(security_plugins_dict['remote_plugins'])

    return all_plugins_dict


def suggest_promptfoo_redteam_plugins_with_openai(purpose: str, plugin_file_path: str = None) -> Dict | str:
    """
    Suggests plugins to test security vulnerabilities based on the purpose of the application using OpenAI.

    Args:
        purpose (str): The purpose of the application.

    Returns:
        List[Dict[str, str]] | str: The list of suggested plugins with descriptions or an error message.
    """
    security_plugins = read_security_plugins(plugin_file_path)
    if isinstance(security_plugins, dict):
        plugins_data = get_security_plugins_list(security_plugins)
    else:
        return security_plugins

    plugins_names_list = list(plugins_data.keys())

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
            model="gpt-4",
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
    write_yaml_file(promptfoo_config_file_name, readteam_config)

    # Generate prompts for redteam
    output_path = f"tmp_{paig_evaluation_app_id}_promptfoo_generated_prompts.yaml"
    command = f"promptfoo redteam generate --max-concurrency 5 --config {promptfoo_config_file_name} --output {output_path}"

    process = run_command_in_background(command)
    wait_for_process_complete(process, verbose=verbose)

    generated_config = read_yaml_file(output_path)

    # Remove temporary files
    os.remove(promptfoo_config_file_name)
    os.remove(output_path)

    return generated_config


def run_promptfoo_redteam_evaluation(eval_id: str, promptfoo_redteam_config: dict, base_prompts: dict = None, custom_prompts: dict = None, verbose: bool = False) -> dict:
    """
    Run the promptfoo redteam evaluation process.

    Args:
        eval_id (str): Evaluation ID.
        promptfoo_redteam_config (dict): Promptfoo redteam configuration.
        base_prompts (dict): Base prompts.
        custom_prompts (dict): Custom prompts.
        verbose (bool): Verbose mode.

    Returns:
        dict: Evaluation report.
    """

    # Create updated promptfoo redteam configuration
    promptfoo_generated_prompts_file_name = f"tmp_{eval_id}_promptfoo_generated_prompts.yaml"

    base_tests = base_prompts.get("tests") if base_prompts else []
    custom_tests = custom_prompts.get("tests") if custom_prompts else []
    promptfoo_redteam_config["tests"] = base_tests + custom_tests + promptfoo_redteam_config["tests"]

    write_yaml_file(promptfoo_generated_prompts_file_name, promptfoo_redteam_config)

    # Run promptfoo redteam evaluation
    output_path = f"tmp_{eval_id}_promptfoo_evaluation_report.json"
    command = f"promptfoo redteam eval --config {promptfoo_generated_prompts_file_name} --output {output_path}"

    process = run_command_in_background(command)
    wait_for_process_complete(process, verbose=verbose)

    # Read evaluation report
    evaluation_report = read_json_file(output_path)

    # Remove temporary files
    os.remove(promptfoo_generated_prompts_file_name)
    os.remove(output_path)

    return evaluation_report