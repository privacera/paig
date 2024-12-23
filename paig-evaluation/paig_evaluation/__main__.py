import sys, os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
import click
from base_paig_eval import run_promptfoo_command_in_background, check_process_status, get_output_from_process
import json


@click.command()
@click.option(
    "--paig_eval_config",
    type=click.STRING,
    default=None,
    help="Path to the PAIG evaluation config file",
)
@click.option(
    "--openai_api_key",
    type=click.STRING,
    default=None,
    help="OpenAI API Key",
)
@click.argument('action', type=click.STRING, required=False)
def main(paig_eval_config: str,  openai_api_key: str, action: str) -> None:
    if action == 'run' or action == 'start':
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
            print("Redteam Report:")
            print(json.dumps(report, indent=2))

        except Exception as e:
            print(f"Error running evaluation: {e}")
    else:
        print("Please provide an action. Options: run|start")


if __name__ == '__main__':
    main()