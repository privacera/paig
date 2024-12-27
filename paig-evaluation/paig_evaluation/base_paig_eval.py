import yaml
import json
import subprocess
import os
import uuid
from typing import Optional
from typing import Dict, Any
from paig_evaluation.utils import get_suggested_plugins, json_to_dict


def create_yaml_from_dict(config_dict, file_name):
    """
    Create a YAML file from a given dictionary and return the file path.
    """
    try:
        with open(file_name, 'w') as yaml_file:
            yaml.dump(config_dict, yaml_file, default_flow_style=False)
        return file_name
    except Exception as e:
        raise RuntimeError(f"Error creating YAML file: {e}")


def run_promptfoo_command_in_background(config_path):
    """
    Run the `promptfoo redteam run` command in the background and return the process object along with paths.
    """
    try:
        # Generate a unique identifier for file names
        unique_id = str(uuid.uuid4())

        # Define paths for the config and output files
        output_path = os.path.join(os.getcwd(), f"output_{unique_id}.json")

        # Create the YAML config file
        # create_yaml_from_dict(config_dict, config_path)


        # Command to run
        command = [
            "promptfoo", "redteam", "run",
            "--no-cache",
            "--max-concurrency", "5",
            "--config", config_path,
            "--output", output_path
        ]

        # Set the environment variable for OpenAI API key
        env = os.environ.copy()
        # env["OPENAI_API_KEY"] = "your_openai_api_key_here"  # Replace with your actual API key

        # Start the process
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        return process, config_path, output_path
    except Exception as e:
        raise RuntimeError(f"Error starting background process: {e}")


def check_process_status(process):
    """
    Check if the process is still running.
    Returns 0 if completed, 1 if running.
    """
    try:
        if process.poll() is None:
            return 1  # Process is running
        return 0  # Process is completed
    except Exception as e:
        raise RuntimeError(f"Error checking process status: {e}")


def read_output_data(output_path):
    if output_path.endswith('.json'):
        with open(output_path, 'r') as file:
            return json.load(file)
    elif output_path.endswith('.yaml'):
        with open(output_path, 'r') as file:
            return yaml.safe_load(file)

def remove_temporary_file(file_path):
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        raise RuntimeError(f"Error removing temporary file: {e}")


def get_output_from_process(output_path: str):
    """
    Retrieve the output JSON file content after the process is completed and clean up files.
    """
    try:
        output_data = read_output_data(output_path)

        # Clean up temporary files
        if os.path.exists(output_path):
            os.remove(output_path)

        return output_data
    except FileNotFoundError:
        raise RuntimeError("Output file not found. The process might have failed.")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error parsing JSON output: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error retrieving output: {e}")


def run_process(paig_eval_config: str, output_directory: str):
    try:

        # Run the command in the background
        process, config_path, output_path = run_promptfoo_command_in_background(paig_eval_config)

        # Check the process status
        while True:
            status = check_process_status(process)
            if status == 0:
                print("Process completed.")
                break
            else:
                output = process.stdout.readline()
                if output:
                    print(output.strip())

        # copy the output file content to paig_eval_output_report.jso
        with open(f'{output_directory}/paig_eval_output_report.json', 'w') as file:
            file.write(open(output_path).read())
        report = get_output_from_process(output_path)
        return json.dumps(report, indent=2)

    except Exception as e:
        print(f"Error running evaluation: {e}")


def generate_config(
        description: str = None,
        targets: Any = None,
        purpose: str = None,
        plugins: Any = None,
        providers: Any = None,
        numTests: int = None,
        language: str = None,
        strategies: Any = None
) -> Dict:
    config_dict = {}
    redteam_dict = {}

    # Get redteam configuration
    redteam_dict["numTests"] = numTests if numTests else 5
    redteam_dict["language"] = language if language else "English"

    if purpose:
        redteam_dict["purpose"] = purpose
    if plugins:
        redteam_dict["plugins"] = plugins
    if providers:
        redteam_dict["providers"] = providers
    if strategies:
        redteam_dict["strategies"] = strategies

    # Get main configuration
    if description:
        config_dict["description"] = description
    if targets:
        config_dict["targets"] = targets

    if redteam_dict:
        config_dict["redteam"] = redteam_dict

    return config_dict


def setup_conf(
        description: str = None,
        targets: Any = None,
        purpose: str = None,
        plugins: Any = None,
        providers: Any = None,
        numTests: int = None,
        language: str = None,
        strategies: Any = None
) -> Dict:
    return generate_config(
        description=description,
        targets=targets,
        purpose=purpose,
        plugins=plugins,
        providers=providers,
        numTests=numTests,
        language=language,
        strategies=strategies
    )

def init_setup_config(application_config):
    try:
        config = json_to_dict(application_config)
        application_name = config.get("application_name")
        application_purpose = config.get("purpose")
        application_client = config.get("application_client", "openai:gpt-4o-mini")

        if not application_purpose or application_purpose == "":
            raise ValueError("Application purpose not found in the configuration file.")
        if not application_name or application_name == "":
            raise ValueError("Application name not found in the configuration file.")

        suggested_plugins = get_suggested_plugins(application_purpose=application_purpose)
        try:
            suggested_plugins_dict = json.loads(suggested_plugins)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {suggested_plugins}") from e
        plugins = suggested_plugins_dict['plugins']
        application_config_dict = {
            "application_name": application_name,
            "purpose": application_purpose,
            "application_client": application_client,
            "categories": plugins
        }
        return application_config_dict
    except Exception as e:
        print(f"Error setting up application config: {e}")


def setup_config(application_config):
    config = json_to_dict(application_config)
    application_name = config.get("application_name")
    application_purpose = config.get("purpose")
    application_client = config.get("application_client")
    categories = config.get("categories")
    if not application_purpose or application_purpose == "":
        raise ValueError("Application purpose not found in the configuration file.")

    targets = [{
        "id": application_client,
        "label": application_name
    }]

    return setup_conf(
        description=application_name,
        targets=targets,
        purpose=application_purpose,
        plugins=categories,
    )


def run_generate_prompts_command_in_background(config_dict):
    try:
        # Generate a unique identifier for file names
        unique_id = str(uuid.uuid4())

        # Define paths for the config and output files
        config_path = os.path.join(os.getcwd(), f"config_with_plugins_{unique_id}.yaml")
        output_path = os.path.join(os.getcwd(), f"output_with_plugins_{unique_id}.yaml")

        # Create the YAML config file
        create_yaml_from_dict(config_dict, config_path)

        # Command to run
        command = [
            "promptfoo", "redteam", "generate",
            "--no-cache",
            "--max-concurrency", "5",
            "--config", config_path,
            "--output", output_path
        ]

        # Set the environment variable for OpenAI API key
        env = os.environ.copy()
        # env["OPENAI_API_KEY"] = "your_openai_api_key_here"  # Replace with your actual API key

        # Start the process
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        return process, config_path, output_path
    except Exception as e:
        raise RuntimeError(f"Error starting background process: {e}")






def generate_prompts(config_with_plugins, output_directory):
    try:
        eval_config = json_to_dict(config_with_plugins)
        # Run the command in the background
        process, config_path, output_path = run_generate_prompts_command_in_background(eval_config)
        # Check the process status
        while True:
            status = check_process_status(process)
            if status == 0:
                print("Process completed.")
                break
            else:
                output = process.stdout.readline()
                if output:
                    print(output.strip())

        # copy the output file content to workdir/paig_eval_config.yaml
        with open(f'{output_directory}/paig_eval_config_with_prompts.yaml', 'w') as file:
            file.write(open(output_path).read())
        remove_temporary_file(config_path)
        report = get_output_from_process(output_path)
        return report

    except Exception as e:
        print(f"Error generating prompts: {e}")
