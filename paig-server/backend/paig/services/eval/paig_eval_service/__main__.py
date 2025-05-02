import uvicorn
import sys, os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)
host = "0.0.0.0"
port = 4547
workers = 1

def main():
    config_path = os.path.join(ROOT_DIR, "conf")
    os.environ["CONFIG_PATH"] = str(config_path)
    try:
        from alembic_db import create_or_update_tables
    except ImportError:
        PAIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        sys.path.append(PAIG_DIR)
        config_path = os.path.join(PAIG_DIR, "conf")
        os.environ["CONFIG_PATH"] = str(config_path)
        from alembic_db import create_or_update_tables
    create_or_update_tables(ROOT_DIR)
    uvicorn.run(
        app="server:app",
        host=host,
        port=port,
        workers=workers,
    )

if __name__ == "__main__":
    main()