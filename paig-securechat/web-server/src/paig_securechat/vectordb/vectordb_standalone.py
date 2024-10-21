import click
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from vectordb.vector_store_factory import VectorStoreFactory
from vectordb.vector_utils import load_vectordb_configs
from core import config

os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@click.command()
@click.option(
    "--config_path",
    type=click.Path(),
    default=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'configs/default_config.yaml')
)
def main(config_path: str):
    if config_path:
        vectordb_config = load_vectordb_configs(config_path)
        config.Config = vectordb_config
    vector_store_factory = VectorStoreFactory(config=config.Config)
    vector_store_factory.create_vectordb_indices()


if __name__ == "__main__":
    main()
