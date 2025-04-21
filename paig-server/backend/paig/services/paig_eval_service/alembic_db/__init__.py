import sys
from alembic.config import Config
from alembic import command
import os
from core.config import load_config_file

config = load_config_file()
database_url = config["database"]["url"]

def create_or_update_tables(root_dir: str = None):
    try:
        if "sqlite+aiosqlite" in database_url:
            db_location = database_url.split("sqlite+aiosqlite:///")[-1]
            if not os.path.exists(db_location):
                os.makedirs(os.path.dirname(db_location), exist_ok=True)
        script_location = "alembic_db"
        if root_dir is not None:
            script_location = os.path.join(root_dir, 'alembic_db')
        alembic_cfg = Config(os.path.join(script_location, 'alembic.ini'))
        alembic_cfg.set_main_option('script_location', script_location)
        command.upgrade(alembic_cfg, 'head')
        print("Tables creation or changes applied on database.")
    except Exception as e:
        print(f"An error occurred during tables creation on database: {e}")
        sys.exit(f"An error occurred during tables creation on database: {e}")
