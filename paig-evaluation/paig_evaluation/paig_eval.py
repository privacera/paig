from paig_evaluation.base_paig_eval import run_process, setup_config, init_setup_config, generate_prompts
import os
import json
import yaml
from typing import Dict


class PaigEval:
    def __init__(self, output_directory=None, openai_api_key=None):
        """
        Initialize the class with an output directory and an optional OpenAI API key.

        Parameters:
            output_directory (str, optional): The directory where output files will be stored.
                                               Defaults to 'workdir' if not provided.
            openai_api_key (str, optional): The OpenAI API key to set in the environment
                                            variable "OPENAI_API_KEY". If not provided or empty,
                                            the key will not be set.
        """
        self.output_directory = output_directory if output_directory else 'workdir'
        self.config_file = None
        self.output_file = None
        if openai_api_key and openai_api_key != "":
            os.environ["OPENAI_API_KEY"] = openai_api_key

    def init_setup(self, application_config):
        """
        Initialize the setup by creating the application config with plugins.
        This method creates the application config with plugins JSON file based
        on the provided application configuration JSON file, under the output directory.

        Args:
            application_config: application configuration JSON.

        Raises:
            FileNotFoundError: If the provided configuration file does not exist.
        """
        if isinstance(application_config, str) and application_config.endswith('.json'):
            if not os.path.exists(application_config):
                raise FileNotFoundError(f"Application config file not found: {application_config}")
        if self.output_directory == 'workdir':
            os.makedirs(self.output_directory, exist_ok=True)
        elif not os.path.exists(self.output_directory):
            raise FileNotFoundError(f"Output directory not found: {self.output_directory}")
        application_config_dict = init_setup_config(application_config)
        # Return JSON dict
        return json.dumps(application_config_dict, indent=4)

    def generate_prompts(self, config_with_plugins):
        """
        Generate `paig_eval_config_with_prompts.yaml` config with prompts using an application configuration file and output directory.

        This method checks for the existence of an application configuration JSON file
        (with plugins included) in the specified output directory. If the file exists,
        it loads the configuration, processes it, and generates prompts based
        configuration and save it into output directory with `paig_eval_config_with_prompts.yaml` file name.

        Raises:
            FileNotFoundError: If the application configuration JSON file is not found.

        """
        if isinstance(config_with_plugins, str) and config_with_plugins.endswith('.json'):
            if not os.path.exists(config_with_plugins):
                raise FileNotFoundError(f"Application config with plugins file not found: {config_with_plugins}")
        application_config_with_plugins_dict = setup_config(config_with_plugins)
        config_file_name = generate_prompts(application_config_with_plugins_dict, self.output_directory)
        self.config_file = config_file_name


    def run(self):
        """
        Execute a process using the PAIG evaluation configuration file and output directory.

        This method verifies the existence of a PAIG evaluation configuration YAML file
        in the specified output directory. If the file exists, it processes the configuration
        and executes a task based on it.

        Raises:
            FileNotFoundError: If the PAIG evaluation configuration YAML file is not found
        """
        paig_eval_config_file = self.config_file
        if not os.path.exists(paig_eval_config_file):
            raise FileNotFoundError(f"PAIG evaluation config file not found: {paig_eval_config_file}")
        output_report, output_report_file_name = run_process(paig_eval_config_file, self.output_directory)
        # Return Report in JSON format
        self.output_file = output_report_file_name
        report_json_data = {}
        try:
            with open(self.output_file, 'r') as f:
                report_json_data =  json.load(f)
        except Exception as e:
            print(f"Error reading output report file: {e}")
        return report_json_data


    def append_user_prompts(self, user_prompts_list: list[Dict]):
        """
        Append user prompts to the existing prompts in the PAIG evaluation configuration file.

        This method appends user prompts to the existing prompts in the PAIG evaluation configuration file.
        The user prompts are provided as a dictionary with the key being the category and the value being a list of prompts.

        Args:
            user_prompts_dict (dict): A dictionary containing user prompts with categories as keys and lists of prompts as values.

        Raises:
            FileNotFoundError: If the PAIG evaluation configuration YAML file is not found.
        """
        try:
            paig_eval_config_file = self.config_file
            if not os.path.exists(paig_eval_config_file):
                raise FileNotFoundError(f"PAIG evaluation config file not found: {paig_eval_config_file}")

            with open(paig_eval_config_file, 'r') as f:
                paig_eval_config = yaml.safe_load(f)

            paig_eval_config['tests'].extend(user_prompts_list)
            # Convert to YAML and write back to the file
            with open(paig_eval_config_file, 'w') as f:
                yaml.dump(paig_eval_config, f)
        except Exception as e:
            print(f"Error appending user prompts: {e}")



