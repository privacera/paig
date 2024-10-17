import click
import os
from vectordb.vector_store_factory import VectorStoreFactory


os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@click.command()
@click.option(
    "--config_path",
    type=click.Path(),
    default=os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'configs/default_config.yaml')
)
def main(config_path: str):
    vector_store_factory = VectorStoreFactory(config=str(config_path))
    vector_store_factory.create_vectordb_indices()


if __name__ == "__main__":
    main()
