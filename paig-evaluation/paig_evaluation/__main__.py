import os
import shutil
import sys
import time

import click

from .promptfoo_utils import ensure_promptfoo_config
from .file_utils import write_yaml_file, read_yaml_file, write_json_file
from .command_utils import run_command_in_foreground
from .paig_evaluator import PAIGEvaluator, get_suggested_plugins, init_setup


@click.command()
@click.option(
    "--application_name",
    type=click.STRING,
    default=None,
    help="Name of the application to evaluate",
)
@click.option(
    "--purpose",
    type=click.STRING,
    default=None,
    help="Purpose of the application",
)
@click.option(
    "--target_id",
    type=click.STRING,
    default=None,
    help="Application target ID for the evaluation",
)
@click.argument('action', type=click.Choice(
    ['init', 'suggest-categories', 'generate-dynamic-prompts', 'evaluate', 'report'],
    case_sensitive=False
), required=True)
@click.option('--verbose', '-v', is_flag=True, default=False, help="Enable verbose output for detailed logs.")
def main(
        action: str,
        verbose: bool,
        application_name: str,
        purpose: str,
        target_id: str
) -> None:
    """
    PAIG Evaluation Tool

    This tool provides an evaluation workflow for the PAIG application.

    ACTIONS:

      init:                     Initialize default configuration file.

      suggest-categories:       Generate plugin category suggestions.

      generate-dynamic-prompts: Create prompts from configurations.

      evaluate:                 Evaluate prompts and save results.

      report:                   Generate and display evaluation report.
    """
    # Define file paths
    application_config_file = "config.yaml"
    suggested_categories_file = "categories.yaml"
    dynamic_prompts_file = "generated-prompts.yaml"
    base_prompts_file = "base-prompts.yaml"
    custom_prompts_file = "custom-prompts.yaml"
    evaluation_report_file = "evaluation-report.json"

    if action == 'init':
        # Initialize the configuration file
        if os.path.exists(application_config_file):
            sys.exit(f"{application_config_file} already exists. Please remove it to create a new one.")
        else:
            paig_evaluator = PAIGEvaluator()
            initial_config = paig_evaluator.init()
            init_setup()

            initial_config.update({
                "application_name": "PAIG Evaluation Application",
                "description": "PAIG Evaluation Application",
                "purpose": "To support IT helpdesk"
            })
            if application_name:
                initial_config["application_name"] = application_name
                initial_config["description"] = application_name
            if purpose:
                initial_config["purpose"] = purpose

            write_yaml_file(application_config_file, initial_config)
            click.echo(f"Configuration initialized and saved to {application_config_file}.")

    elif action == "suggest-categories":
        # Suggest plugin categories
        if not os.path.exists(application_config_file):
            sys.exit(f"Configuration file {application_config_file} not found. Please run 'init' first.")

        application_config = read_yaml_file(application_config_file)
        suggested_categories = get_suggested_plugins(application_config["purpose"])

        write_yaml_file(suggested_categories_file, suggested_categories['result'])
        click.echo(f"Suggested categories saved to {suggested_categories_file}.")

    elif action == "generate-dynamic-prompts":
        # Generate dynamic prompts
        if not os.path.exists(application_config_file) or not os.path.exists(suggested_categories_file):
            sys.exit(
                f"Required files not found. Ensure both {application_config_file} and {suggested_categories_file} exist.")

        application_config = read_yaml_file(application_config_file)
        suggested_categories = read_yaml_file(suggested_categories_file)
        targets = [
            {
                "id": target_id if target_id else "openai:gpt-4o-mini",
                "label": application_config["application_name"]
            }
        ]

        paig_evaluator = PAIGEvaluator()
        suggested_plugins_names_list = [plugin['Name'] for plugin in suggested_categories]
        generated_prompts = paig_evaluator.generate_prompts(
            application_config,
            suggested_plugins_names_list,
            targets=targets,
            verbose=verbose
        )

        write_yaml_file(dynamic_prompts_file, generated_prompts['result'])
        click.echo(f"Generated prompts saved to {dynamic_prompts_file}.")

    elif action == "evaluate":
        # Evaluate prompts
        if not os.path.exists(application_config_file) or not os.path.exists(dynamic_prompts_file):
            sys.exit(
                f"Required files not found. Ensure both {application_config_file} and {dynamic_prompts_file} exist.")

        application_config = read_yaml_file(application_config_file)
        email = application_config.get("email", "support@privacera.com")
        ensure_promptfoo_config(email)

        generated_prompts = read_yaml_file(dynamic_prompts_file)

        # Optional base and custom prompts
        base_prompts = read_yaml_file(base_prompts_file) if os.path.exists(base_prompts_file) else None
        custom_prompts = read_yaml_file(custom_prompts_file) if os.path.exists(custom_prompts_file) else None

        paig_evaluator = PAIGEvaluator()
        evaluation_results = paig_evaluator.evaluate(
            application_config["paig_eval_id"],
            generated_prompts,
            base_prompts,
            custom_prompts,
            verbose=verbose
        )

        # Copy all the files used for evaluation to the evaluation directory
        timestamp_str = time.strftime("%Y%m%d_%H%M%S")

        # Create directory for the current evaluation
        evaluation_dir = f"evaluations/{timestamp_str}"
        os.makedirs(evaluation_dir, exist_ok=True)

        shutil.copy(application_config_file, f"{evaluation_dir}/{application_config_file}")
        shutil.copy(suggested_categories_file, f"{evaluation_dir}/{suggested_categories_file}")
        shutil.copy(dynamic_prompts_file, f"{evaluation_dir}/{dynamic_prompts_file}")

        if os.path.exists(base_prompts_file):
            shutil.copy(base_prompts_file, f"{evaluation_dir}/{base_prompts_file}")

        if os.path.exists(custom_prompts_file):
            shutil.copy(custom_prompts_file, f"{evaluation_dir}/{custom_prompts_file}")

        write_json_file(f"{evaluation_dir}/{evaluation_report_file}", evaluation_results['result'])
        click.echo(f"Evaluation report saved to {evaluation_dir}/{evaluation_report_file}.")

    elif action == "report":
        # Generate and display reports
        report_server_command = "promptfoo redteam report"
        run_command_in_foreground(report_server_command, verbose=verbose)
        click.echo("Report generation completed.")


if __name__ == '__main__':
    main()
