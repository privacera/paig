import os
import sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
import logging
import click
import uvicorn
from database_setup import create_or_update_tables
from core.utils import set_up_standalone_mode

# Configure logging
logger = logging.getLogger(__name__)

@click.command()
@click.option(
    "--host",
    type=click.STRING,
    default="0.0.0.0",
    help="Host to run the server on",
)
@click.option(
    "--port",
    type=click.INT,
    default=3535,
    help="Port to run the server on",
)
@click.option(
    "--config_path",
    type=click.Path(),
    help="Absolute Path to the configuration folder",
)
@click.option(
    "--custom_config_path",
    type=click.Path(),
    default=None,
    help="Absolute Path to the custom configuration folder",
)
@click.option(
    "--debug",
    type=click.BOOL,
    default=False,
    help="Enable debug mode",
)
@click.option(
    "--disable_paig_shield_plugin",
    type=click.BOOL,
    default=False,
    help="Disable the Paig Shield Plugin",
)
@click.option(
    "--openai_api_key",
    type=click.STRING,
    default=None,
    help="OpenAI API Key for the server",
)
@click.argument('action', type=click.STRING, required=False)
def main(debug: bool,
         config_path: str,
         custom_config_path: str,
         host: str,
         port: int,
         disable_paig_shield_plugin,
         openai_api_key,
         action: str
         ) -> None:
    def _is_colab():
        try:
            import google.colab
        except ImportError:
            return False
        try:
            from IPython.core.getipython import get_ipython
        except ImportError:
            return False
        return True
    try:
        set_up_standalone_mode(
            ROOT_DIR,
            debug,
            config_path,
            custom_config_path,
            disable_paig_shield_plugin,
            host,
            port,
            openai_api_key,
            single_user_mode=_is_colab()
        )

        if not os.path.exists("securechat"):
            os.makedirs("securechat")

        if action == 'create_tables':
            create_or_update_tables(ROOT_DIR)
        elif action == 'run':
            create_or_update_tables(ROOT_DIR)
            # Start Uvicorn server
            uvicorn.run(
                app="app.server:app",
                host=host,
                port=port,
                workers=1,
            )
        else:
            print("Please provide an action. Options: create_tables, run")

    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}", exc_info=True)  # Log with full traceback
        print("Error: The application failed to start. Please try again later.")
        sys.exit(1)  # Exit with error code


if __name__ == "__main__":
    main()
