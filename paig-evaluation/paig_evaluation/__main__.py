import json
import sys, os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
import click
from base_paig_eval import run_process, setup_config, init_setup_config


@click.command()
@click.option(
    "--paig_eval_config",
    type=click.STRING,
    default=None,
    help="Path to the PAIG evaluation config file",
)
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
def main(paig_eval_config: str,  application_config:str, openai_api_key: str, action: str) -> None:
    if action == 'run' or action == 'start':
        report = run_process(paig_eval_config, openai_api_key)
        print(f"Redteam Report:: {report}")
    elif action == 'init_setup':
        if application_config is None or application_config == "":
            raise ValueError("Please provide the path to the application config file.")

        application_config_dict = init_setup_config(application_config)
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
        eval_config = json.dumps(eval_config_dict, indent=2)
        print(f"PAIG Eval Config: {eval_config}")
    else:
        print("Please provide an action. Options: run|start or setup")


if __name__ == '__main__':
    main()