import yaml
import json
import subprocess
import os
import uuid
from typing import Optional

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