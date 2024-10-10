from langchain_community.vectorstores.opensearch_vector_search import OpenSearchVectorSearch
from vectordb.vector_store_interface import VectorStoreIndex
from vectordb.vector_utils import (
    get_all_files, get_loaders, create_documents,
    delete_extracted_directory, is_valid_data_path)
from core import config

import json
import boto3
import vectordb.opensearch as opensearch
import logging
import os
import sys

logger = logging.getLogger(__name__)


class OpensearchVectorStore(VectorStoreIndex):
    def __init__(self, vectordb_config, embeddings):
        self.config = config.Config
        self.data_path = vectordb_config['data_path']
        self.index_name = vectordb_config['index_name']
        opensearch_config = self.config["opensearch"]
        self.user = opensearch_config.get("user")
        self.password = opensearch_config.get("password")
        self.embedding_client = 'openai'
        domain_name = opensearch_config.get("domain_name")
        region = opensearch_config.get("region")
        hosts = opensearch_config.get("hosts")
        self.langchain_embedding_client = embeddings
        if "bedrock" in self.config:
            llm_conf = self.config["bedrock"]
            self.embedding_model_name = llm_conf.get("embedding_model")
            llm_region = llm_conf.get("region")
            self.bedrock_client = boto3.client("bedrock-runtime", region_name=llm_region)


        if domain_name and region:
            # We will dynamically get the host and passsword. User is the same as the domain name
            self.user = domain_name
            self.password = opensearch.get_secret(domain_name, region)
            hosts = opensearch.get_opensearch_endpoint(domain_name, region)

        self.opensearch_indexer_client = opensearch.get_opensearch_cluster_client(hosts, self.user, self.password,
                                                                                  self.index_name)

        #TODO: This might have issues when there is multi node OpenSearch cluster
        self.opensearch_url=f"https://{hosts}"
        # Not sure what this is for
        self._is_aoss = False
        self.opensearch_langchain_retriever_client = OpenSearchVectorSearch(
            index_name=self.index_name,
            embedding_function=self.langchain_embedding_client,
            opensearch_url=self.opensearch_url,
            http_auth=(self.user, self.password),
            is_aoss=self._is_aoss,
            verify_certs=False,
            ssl_show_warn=False
        )


    def create_vector_embedding_with_bedrock(self, text, index_name):
        payload = {"inputText": f"{text}"}
        body = json.dumps(payload)
        modelId = self.embedding_model_name
        accept = "application/json"
        contentType = "application/json"

        response = self.bedrock_client.invoke_model(
            body=body, modelId=modelId, accept=accept, contentType=contentType
        )
        response_body = json.loads(response.get("body").read())

        embedding = response_body.get("embedding")
        return {"_index": index_name, "text": text, "vector_field": embedding}

    def create_vector_embedding_with_openai(self, docs, index_name):
        docsearch = OpenSearchVectorSearch.from_documents(
            docs,
            self.langchain_embedding_client,
            index_name=index_name,
            opensearch_url=self.opensearch_url,
            http_auth=(self.user, self.password),
            is_aoss=self._is_aoss,
            verify_certs=False,
            ssl_show_warn=False
        )
        return {"_index": index_name, "text": docs, "vector_field": docsearch.embeddings}

    def create_vector_db(self):
        pass

    def get_vector_store_index(self, recreate_index=False):
        if recreate_index and is_valid_data_path(self.data_path):
            logging.info(f"Recreating index, since recreate_index={recreate_index}")
            response = opensearch.delete_opensearch_index(self.opensearch_indexer_client, self.index_name)
            if response:
                logger.info("OpenSearch index successfully deleted")
        logging.info(f"Checking if index {self.index_name} exists in OpenSearch cluster")
        exists = opensearch.check_opensearch_index(self.opensearch_indexer_client, self.index_name)
        if not exists and is_valid_data_path(self.data_path):
            logging.info(f"Creating OpenSearch index {self.index_name}...")
            success = opensearch.create_index(self.opensearch_indexer_client, self.index_name)
            if success:
                logging.info(f"Creating OpenSearch index {self.index_name} mapping")
                success = opensearch.create_index_mapping(self.opensearch_indexer_client, self.index_name)
                logging.info(f"OpenSearch Index mapping created response={success}")
            initial_contents = set(os.listdir(self.data_path))
            logger.info(f"Data path initial content::{initial_contents}")
            all_files = get_all_files(self.data_path)

            if self.embedding_client == 'bedrock':
                all_records = []
                for file_tupple in all_files:
                    file = file_tupple[0]
                    file_path = file_tupple[1]
                    logging.info(f"Adding documents from file {file} with path {file_path}")
                    with open(file_path, 'r') as data_file:
                        data_contents = data_file.read()
                        all_records.append(data_contents)
                        logging.info(f"Appended data from '{file_path}' to the list.")

                # Vector embedding using Amazon Bedrock Titan text embedding
                logging.info(f"Creating embeddings for records, count={len(all_records)}")

                all_vector_embeddings = []
                i = 0
                for record in all_records:
                    i += 1
                    records_with_embedding = self.create_vector_embedding_with_bedrock(record, self.index_name)

                    logging.info(f"Embedding for record {i} created")
                    all_vector_embeddings.append(records_with_embedding)
                    if i % 500 == 0 or i == len(all_records) - 1:
                        # Bulk put all records to OpenSearch
                        success, failed = opensearch.put_bulk_in_opensearch(all_vector_embeddings,
                                                                            self.opensearch_indexer_client)
                        all_vector_embeddings = []
                        logging.info(f"Documents saved {success}, documents failed to save {failed}")
            else:
                loaders = []
                documents = []
                if all_files:
                    loaders = get_loaders(all_files)
                if loaders:
                    documents = create_documents(loaders)
                chunks = self.chunk_list(documents, 500)
                for chunk in chunks:
                    self.create_vector_embedding_with_openai(chunk, self.index_name)
            final_contents = set(os.listdir(self.data_path))
            new_contents = final_contents - initial_contents
            delete_extracted_directory(new_contents, self.data_path)
            logging.info("Finished adding documents to VectorDB")

        return self.opensearch_langchain_retriever_client

    def chunk_list(self, input_list, chunk_size):
        return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]
