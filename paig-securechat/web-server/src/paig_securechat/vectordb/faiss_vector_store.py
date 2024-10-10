from vectordb.vector_store_interface import VectorStoreIndex
from langchain_community.vectorstores import FAISS
from vectordb.vector_utils import (
    is_directory_empty, get_all_files, get_loaders, create_documents, directory_clean_up,
    delete_extracted_directory, is_valid_data_path)

import logging
import os
import sys


logger = logging.getLogger(__name__)


class FaissVectorStore(VectorStoreIndex):
    def __init__(self, vector_db_config, embeddings):
        self.data_path = vector_db_config['data_path']
        self.index_path = vector_db_config['index_path']
        self.embeddings = embeddings

    def create_vector_db(self):
        initial_contents = set(os.listdir(self.data_path))
        logger.info(f"Data path initial content::{initial_contents}")
        loaders = []
        documents = []
        files = get_all_files(self.data_path)
        if files:
            loaders = get_loaders(files)
        if loaders:
            documents = create_documents(loaders)
        if documents:
            logger.info(f"Creating FAISS Vector_DB with documents")
            vectordb = FAISS.from_documents(
                documents, self.embeddings
            )
            vectordb.save_local(self.index_path)
        else:
            logger.info(f"Data path {self.data_path} is empty.")
            logger.info(f"Creating FAISS Vector_DB without documents")
            texts = ["FAISS is an important library", "LangChain supports FAISS"]
            vectordb = FAISS.from_texts(texts, self.embeddings)
            vectordb.save_local(self.index_path)
        final_contents = set(os.listdir(self.data_path))
        logger.info(f"Data path final contents after extraction::{initial_contents}")
        new_contents = final_contents - initial_contents
        logger.info(f"Data path new extracted contents::{new_contents}")
        delete_extracted_directory(new_contents, self.data_path)
        return vectordb

    def get_vector_store_index(self, recreate_index=False):
        if recreate_index and is_valid_data_path(self.data_path):
            directory_clean_up(self.index_path)
            logger.info("Directory clean up done.")
        if is_directory_empty(self.index_path):
            logger.info("Rebuilding index...")
            if is_valid_data_path(self.data_path):
                vectordb = self.create_vector_db()
        else:
            logger.info("Index already exists, so won't rebuild it, just reload it")
            vectordb = FAISS.load_local(self.index_path, self.embeddings, allow_dangerous_deserialization=True)
        return vectordb
