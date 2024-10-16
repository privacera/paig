import sys

from vectordb.vector_store_interface import VectorStoreIndex
from langchain_community.vectorstores import Chroma
from vectordb.vector_utils import (
    is_directory_empty, get_all_files, get_loaders, create_documents, directory_clean_up,
    delete_extracted_directory, is_valid_data_path)

import logging
import os


logger = logging.getLogger(__name__)


class ChromaVectorStore(VectorStoreIndex):
    def __init__(self, vectordb_config, embeddings):
        self.data_path = vectordb_config['data_path']
        self.index_path = vectordb_config['index_path']
        self.embeddings = embeddings

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
            logger.info(f"Creating Chroma Vector_DB with documents")
            vectordb = Chroma.from_documents(documents, embedding=self.embeddings,
                                             persist_directory=self.index_path)
        else:
            logger.info(f"Data path {self.data_path} is empty.")
            logger.info(f"Creating Chroma Vector_DB without documents")
            vectordb = Chroma(embedding_function=self.embeddings, persist_directory=self.index_path)
        final_contents = set(os.listdir(self.data_path))
        logger.info(f"Data path final contents after extraction::{final_contents}")
        new_contents = final_contents - initial_contents
        logger.info(f"Data path new extracted contents::{new_contents}")
        delete_extracted_directory(new_contents, self.data_path)
        return vectordb

    def get_vector_store_index(self, recreate_index=False):
        if recreate_index and is_valid_data_path(self.data_path):
            directory_clean_up(self.index_path)
        if is_directory_empty(self.index_path):
            logger.info("Rebuilding index...")
            if is_valid_data_path(self.data_path):
                vectordb = self.create_vector_db()
        else:
            logger.info("Index already exists, so won't rebuild it, just reload it")
            vectordb = Chroma(persist_directory=self.index_path, embedding_function=self.embeddings)
        return vectordb
