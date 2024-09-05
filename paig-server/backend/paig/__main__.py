import asyncio
import os
import sys
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

import click
import uvicorn


@click.command()
@click.option(
    "--host",
    type=click.STRING,
    default="127.0.0.1",
    help="Host to run the server on",
)
@click.option(
    "--port",
    type=click.INT,
    default=4545,
    help="Port to run the server on",
)
@click.option(
    "--config_path",
    type=click.Path(),
    default=None,
    help="Absolute Path to the configuration folder",
)
@click.option(
    "--custom_config_path",
    type=click.Path(),
    default=None,
    help="Absolute Path to the custom configuration folder",
)
@click.option(
    "--paig_deployment",
    type=click.STRING,
    default="dev",
    help="Paig deployment environment",
)
@click.option(
    "--workers",
    type=click.INT,
    default=1,
    help="Configure number of workers for the server",
)
@click.argument('action', type=click.STRING, required=False)
def main(
         host: str,
         port: int,
         config_path: str,
         custom_config_path: str,
         paig_deployment: str,
         action: str,
         workers: int
         ) -> None:

    set_up_standalone_mode(
        host,
        port,
        config_path,
        custom_config_path,
        paig_deployment,
        ROOT_DIR
    )
    cleanup()
    from alembic_db import create_or_update_tables, create_default_user_and_ai_application
    from api.encryption.events.startup import create_default_encryption_keys
    if action == 'create_tables':
        create_or_update_tables(ROOT_DIR)
    if action == 'run':
        create_or_update_tables(ROOT_DIR)
        create_default_user_and_ai_application()
        asyncio.run(create_default_encryption_keys())
        uvicorn.run(
            app="server:app",
            host=host,
            port=port,
            workers=workers,
        )
    else:
        return print("Please provide an action. Options: create_tables or run")


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



def set_up_standalone_mode(
        host,
        port,
        config_path,
        custom_config_path,
        paig_deployment,
        ROOT_DIR
):
    from core import constants
    constants.SINGLE_USER_MODE = _is_colab()
    constants.HOST = host
    constants.PORT = port
    constants.MODE = "standalone"
    if config_path is None:
        config_path = os.path.join(ROOT_DIR, "conf")
    if custom_config_path is None:
        custom_config_path = 'custom-conf'
    os.environ["CONFIG_PATH"] = str(config_path)
    os.environ["EXT_CONFIG_PATH"] = str(custom_config_path)
    os.environ["PAIG_ROOT_DIR"] = str(ROOT_DIR)
    if paig_deployment:
        os.environ["PAIG_DEPLOYMENT"] = str(paig_deployment)


def cleanup():
    import atexit
    import shutil
    import os
    import fasteners
    from core import constants
    lock = fasteners.InterProcessLock(constants.SCHEDULER_LOCK)
    atexit.register(lock.release)
    _temp_dir = os.path.join(ROOT_DIR, constants.TEMP_DIR)
    if os.path.exists(_temp_dir):
        shutil.rmtree(_temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
