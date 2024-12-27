from paig_evaluation.base_paig_eval import run_process, setup_config, init_setup_config, generate_prompts
import os
import json


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
        if openai_api_key and openai_api_key != "":
            os.environ["OPENAI_API_KEY"] = openai_api_key

    def init_setup(self, application_config):
        """
        Initialize the setup by creating the application config with plugins.
        This method creates the application config with plugins JSON file based
        on the provided application configuration JSON file, under the output directory.

        Args:
            application_config (str): Path to the application configuration JSON file.

        Raises:
            FileNotFoundError: If the provided configuration file does not exist.
        """
        application_config_json_file = "application_config.json"
        if application_config:
            application_config_json_file = application_config
        if application_config_json_file.endswith('.json'):
            if not os.path.exists(application_config_json_file):
                raise FileNotFoundError(f"Application config file not found: {application_config_json_file}")
        application_config_dict = init_setup_config(application_config_json_file)
        if self.output_directory == 'workdir':
            os.makedirs(self.output_directory, exist_ok=True)
        with open(f'{self.output_directory}/application_config_with_plugins.json', 'w') as file:
            json.dump(application_config_dict, file, indent=2)

    def generate_prompts(self):
        """
        Generate `paig_eval_config_with_prompts.yaml` config with prompts using an application configuration file and output directory.

        This method checks for the existence of an application configuration JSON file
        (with plugins included) in the specified output directory. If the file exists,
        it loads the configuration, processes it, and generates prompts based
        configuration and save it into output directory with `paig_eval_config_with_prompts.yaml` file name.

        Raises:
            FileNotFoundError: If the application configuration JSON file is not found.

        """
        application_config_with_plugins_json_file = f"{self.output_directory}/application_config_with_plugins.json"
        if not os.path.exists(application_config_with_plugins_json_file):
            raise FileNotFoundError(f"Application config with plugins file not found: {application_config_with_plugins_json_file}")
        application_config_with_plugins_dict = setup_config(application_config_with_plugins_json_file)
        generate_prompts(application_config_with_plugins_dict, self.output_directory)

    def run(self):
        """
        Execute a process using the PAIG evaluation configuration file and output directory.

        This method verifies the existence of a PAIG evaluation configuration YAML file
        in the specified output directory. If the file exists, it processes the configuration
        and executes a task based on it.

        Raises:
            FileNotFoundError: If the PAIG evaluation configuration YAML file is not found
        """
        paig_eval_config_file = f"{self.output_directory}/paig_eval_config_with_prompts.yaml"
        if not os.path.exists(paig_eval_config_file):
            raise FileNotFoundError(f"PAIG evaluation config file not found: {paig_eval_config_file}")
        run_process(paig_eval_config_file, self.output_directory)



