import yaml
import json
import subprocess
import os
import uuid
from typing import Optional
from typing import Dict, Any
from utils import get_suggested_plugins


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


def run_promptfoo_command_in_background(config_dict):
    """
    Run the `promptfoo redteam run` command in the background and return the process object along with paths.
    """
    try:
        # Generate a unique identifier for file names
        unique_id = str(uuid.uuid4())

        # Define paths for the config and output files
        config_path = os.path.join(os.getcwd(), f"config_{unique_id}.yaml")
        output_path = os.path.join(os.getcwd(), f"output_{unique_id}.json")

        # Create the YAML config file
        create_yaml_from_dict(config_dict, config_path)

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


def get_output_from_process(output_path: str, config_path: Optional[str] = None):
    """
    Retrieve the output JSON file content after the process is completed and clean up files.
    """
    try:
        with open(output_path, 'r') as output_file:
            output_data = json.load(output_file)

        # Clean up temporary files
        if config_path and os.path.exists(config_path):
            os.remove(config_path)
        if os.path.exists(output_path):
            os.remove(output_path)

        return output_data
    except FileNotFoundError:
        raise RuntimeError("Output file not found. The process might have failed.")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error parsing JSON output: {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error retrieving output: {e}")


def run_process(paig_eval_config: str,  openai_api_key: str):
    try:
        if paig_eval_config is None or paig_eval_config == "":
            raise ValueError("Please provide the path to the PAIG evaluation config file.")

        # Set the OpenAI API key as an environment variable
        if openai_api_key and openai_api_key != "":
            os.environ["OPENAI_API_KEY"] = openai_api_key

        # Load the config file
        with open(paig_eval_config, "r") as file:
            eval_config = json.load(file)

        # Run the command in the background
        process, config_path, output_path = run_promptfoo_command_in_background(eval_config)

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

        report = get_output_from_process(output_path, config_path)
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
    with open(application_config, 'r') as file:
        config = json.load(file)
        application_name = config.get("application_name")
        application_purpose = config.get("purpose")
        application_client = config.get("application_client")
    if not application_purpose or application_purpose == "":
        raise ValueError("Application purpose not found in the configuration file.")

    suggested_plugins = get_suggested_plugins(application_purpose=application_purpose)
    suggested_plugins_dict = json.loads(suggested_plugins)
    plugins = suggested_plugins_dict['plugins']
    application_config_dict = {
        "application_name": application_name,
        "purpose": application_purpose,
        "application_client": application_client,
        "categories": plugins
    }
    return application_config_dict


def setup_config(application_config):
    with open(application_config, 'r') as file:
        config = json.load(file)
        application_name = config.get("application_name")
        application_purpose = config.get("purpose")
        application_client = config.get("application_client")
        categories = config.get("categories")
    if not application_purpose or application_purpose == "":
        raise ValueError("Application purpose not found in the configuration file.")

    targets = {
        "id": application_client,
        "label": application_name
    }

    return setup_conf(
        description=application_name,
        targets=targets,
        purpose=application_purpose,
        plugins=categories,
    )
