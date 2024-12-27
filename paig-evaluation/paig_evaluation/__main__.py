import json
import sys, os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
import click
from base_paig_eval import run_process, setup_config, init_setup_config, generate_prompts


@click.command()
@click.option(
    "--application_config",
    type=click.STRING,
    default=None,
    help="Path to the Application config file",
)
@click.option(
    "--openai_api_key",
    type=click.STRING,
    default=None,
    help="OpenAI API Key",
)
@click.argument('action', type=click.STRING, required=False)
def main(application_config:str, openai_api_key: str, action: str) -> None:
    # Set the OpenAI API key as an environment variable
    if openai_api_key and openai_api_key != "":
        os.environ["OPENAI_API_KEY"] = openai_api_key

    if action == 'run' or action == 'start':
        eval_config = "workdir/paig_eval_config_with_prompts.yaml"
        if eval_config.endswith('.yaml'):
            if not os.path.exists(eval_config):
                sys.exit("Please provide a valid path to the PAIG evaluation config file. Run 'paig-evaluation setup' to create the config file.")
        report = run_process(eval_config, 'workdir')
    elif action == 'init_setup':
        application_config_json_file = "application_config.json"
        if application_config:
            application_config_json_file = application_config
        application_config_dict = init_setup_config(application_config_json_file)
        # make workdir and create output_with_plugins.json
        os.makedirs('workdir', exist_ok=True)

        with open('workdir/application_config_with_plugins.json', 'w') as file:
            json.dump(application_config_dict, file, indent=2)
    elif action == 'setup':
        application_config = "workdir/application_config_with_plugins.json"
        # check if the application config file exists
        if not os.path.exists(application_config):
            sys.exit("Please run init_setup action to create the application config file.")
        eval_config_dict = setup_config(application_config)
        with open('workdir/application_setup_config.json', 'w') as file:
            json.dump(eval_config_dict, file, indent=2)
    elif action == 'generate':
        application_setup_config = "workdir/application_setup_config.json"
        # check if the application config file exist
        if application_setup_config.endswith('.json'):
            if not os.path.exists(application_setup_config):
                sys.exit(
                    "Please provide a valid path to the PAIG evaluation config file. Run 'paig-evaluation setup' to create the config file.")

        generate_prompts(application_setup_config, 'workdir')
    else:
        print("Please provide an action. Options: run|start or setup")


if __name__ == '__main__':
    main()