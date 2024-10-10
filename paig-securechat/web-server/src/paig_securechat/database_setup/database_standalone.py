import os
import click
from database_setup import create_or_update_tables

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@click.command()
@click.option(
    "--secure_chat_deployment",
    type=click.STRING,
    default="dev",
)
@click.option(
    "--config_path",
    type=click.Path(),
    default=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'configs'),
)
def db_setup(secure_chat_deployment: str, config_path: str):
    os.environ["SECURE_CHAT_DEPLOYMENT"] = secure_chat_deployment
    os.environ["CONFIG_PATH"] = str(config_path)
    create_or_update_tables()


if __name__ == '__main__':
    db_setup()
