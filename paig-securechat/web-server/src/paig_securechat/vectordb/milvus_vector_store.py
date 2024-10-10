from langchain.vectorstores.milvus import Milvus
from pymilvus import MilvusClient
from core import config
from vectordb.vector_store_interface import VectorStoreIndex
from vectordb.vector_utils import get_all_files, get_loaders, create_documents, delete_extracted_directory, is_valid_data_path
import logging
import os
import sys


logger = logging.getLogger(__name__)


class MilvusVectorStore(VectorStoreIndex):
    def __init__(self, vector_db_config, embeddings):
        self.data_path = vector_db_config['data_path']
        self.collection_name = vector_db_config['collection_name']
        self.embeddings = embeddings
        self.config = config.Config
        milvus_config = self.config.get("milvus")
        self.MILVUS_USER = milvus_config.get("user")
        self.MILVUS_PASSWORD = milvus_config.get("password")
        self.MILVUS_HOST = milvus_config.get("host")
        self.MILVUS_PORT = milvus_config.get("port")
        self.MILVUS_DATABASE = milvus_config.get("database")
        self.connection_args = {"user": self.MILVUS_USER, "password": self.MILVUS_PASSWORD,
                                "database": self.MILVUS_DATABASE, "host": self.MILVUS_HOST, "port": self.MILVUS_PORT, }
        self.vector_store = None
        logger.info(f"Milvus data_path={self.data_path} ")
        logger.info(f"Milvus collection_name={self.collection_name} ")
        logger.info(f"Milvus DB HOST={self.MILVUS_HOST} ")
        logger.info(f"Milvus DB PORT={self.MILVUS_PORT} ")

    def get_milvus_client(self):
        return MilvusClient(
            uri=f"http://{self.MILVUS_HOST}:{self.MILVUS_PORT}",
            user=self.MILVUS_USER,
            password=self.MILVUS_PASSWORD,
            db_name=self.MILVUS_DATABASE
        )

    def get_milvus_collection(self):
        return Milvus(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                connection_args=self.connection_args
            )

    def create_vector_db(self):
        initial_contents = set(os.listdir(self.data_path))
        logger.info(f"Data path initial content::{initial_contents}")
        files = []
        loaders = []
        documents = []
        if self.data_path:
            files = get_all_files(self.data_path)
        if files:
            loaders = get_loaders(files)
        if loaders:
            documents = create_documents(loaders)
        if documents:
            logger.info(f"Creating Milvus Vector_DB with documents")
            # TODO: Collection create and use same collection
            # milvus_client.create_collection(collection_name=self.collection_name, dimension=512, auto_id=True)
            chunks = self.chunk_list(documents, 500)
            for chunk in chunks:
                self.vector_store = Milvus.from_documents(
                    documents=chunk,
                    embedding=self.embeddings,
                    collection_name=self.collection_name,
                    connection_args=self.connection_args
                )
        final_contents = set(os.listdir(self.data_path))
        logger.info(f"Data path final contents after extraction::{initial_contents}")
        new_contents = final_contents - initial_contents
        logger.info(f"Data path new extracted contents::{new_contents}")
        delete_extracted_directory(new_contents, self.data_path)

    def chunk_list(self, input_list, chunk_size):
        return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]

    def get_vector_store_index(self, recreate_index=False):
        milvus_client = self.get_milvus_client()
        if recreate_index and is_valid_data_path(self.data_path):
            logger.info(f"Recreating Milvus collection, since recreate_index={recreate_index}")
            if self.collection_name in milvus_client.list_collections():
                logger.info("Milvus collection already exists, so dropping it")
                milvus_client.drop_collection(self.collection_name)
            self.create_vector_db()
        else:
            logger.info(f"Checking if index {self.collection_name} exists in Milvus cluster")
            if self.collection_name in milvus_client.list_collections():
                logger.info("Index already exists, so won't rebuild it, just reload it")
                self.vector_store = Milvus(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    connection_args=self.connection_args
                )
            else:
                logger.info("Rebuilding Milvus Vector Store...")
                if is_valid_data_path(self.data_path):
                    self.create_vector_db()
        return self.vector_store
