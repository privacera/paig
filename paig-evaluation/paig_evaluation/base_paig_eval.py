import yaml
import json
import subprocess
import os
import uuid
from typing import Optional
from typing import Dict, Any


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
    if purpose:
        redteam_dict["purpose"] = purpose
    if plugins:
        redteam_dict["plugins"] = plugins
    if numTests:
        redteam_dict["numTests"] = numTests
    if providers:
        redteam_dict["providers"] = providers
    if language:
        redteam_dict["language"] = language
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


def setup(
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


def setup_config(application_config):
    with open(application_config, 'r') as file:
        config = json.load(file)
        description = config.get('description', 'My Eval')
        purpose = config.get('purpose', 'To evaluate the performance of the chatbot')
        plugins = config.get('plugins', ["pii"])
        providers = config.get('providers', ["openai:gpt-4o-mini"])
        numTests = config.get('numTests', 1)
        language = config.get('language', 'English')
        targets = config.get('targets', [
            {
                "id": "openai:gpt-4o-mini",
                "label": "unsafe chat"
            }
        ])
        strategies = config.get('strategies', [])

    return setup(
        description=description,
        targets=targets,
        purpose=purpose,
        plugins=plugins,
        providers=providers,
        numTests=numTests,
        language=language,
        strategies=strategies
    )
