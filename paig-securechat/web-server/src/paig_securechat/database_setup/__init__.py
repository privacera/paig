import sys
from alembic.config import Config
from alembic import command
import os


def create_or_update_tables(ROOT_DIR: str = None):
    try:
        script_location = "database_setup"
        if ROOT_DIR is not None:
            script_location = os.path.join(ROOT_DIR, 'database_setup')
        alembic_cfg = Config(os.path.join(script_location, 'alembic.ini'))
        alembic_cfg.set_main_option('script_location', script_location)
        command.upgrade(alembic_cfg, 'head')
        print(f"Tables creation or changes applied on database.")
    except Exception as e:
        print(f"An error occurred during tables creation on database: {e}")
        sys.exit(f"An error occurred during tables creation on database: {e}")