import sys
from vectordb.vector_utils import VectorConfig
import logging
from vectordb.vector_utils import get_embedding_client, get_langchain_embedding_client
import os

logger = logging.getLogger(__name__)


_MilvusVectorStore = None
_OpensearchVectorStore = None
_FaissVectorStore = None
_ChromaVectorStore = None

class VectorStoreFactory(VectorConfig):
    def __init__(self, config):
        logger.info(f"Initialising VectorStoreFactory properties.")
        VectorConfig.__init__(self, config)
        self.vector_indices_map = {}

    def create_vectordb_indices(self):
        for ai_application in self.ai_applications:
            embedding_client = get_embedding_client(ai_application)
            embeddings = get_langchain_embedding_client(embedding_client)
            vectordb_index = self.get_vectordb_index(ai_application, embeddings)
            self.vector_indices_map[ai_application] = vectordb_index

    def get_application_vectordb_index(self, app_name):
        vectordb_index = self.vector_indices_map.get(app_name, None)
        if vectordb_index is None:
            logger.error(f"VectorDB index not found for {app_name}")
            sys.exit(f"VectorDB index not found for {app_name}")
        return vectordb_index

    def get_vectordb_index(self, ai_app_name, embeddings):
        logger.info(f"Initialising vector store index.")
        ai_app_config = self.cnf["AI_applications"][ai_app_name]
        vector_store = None
        vector_db_config = ai_app_config["vectordb"]
        vector_type = vector_db_config["vector_type"]
        recreate_index = vector_db_config['recreate_index'] if 'recreate_index' in vector_db_config else False
        if vector_type == "chroma":
            global _ChromaVectorStore
            if _ChromaVectorStore is None:
                """ Chroma anonymous usage information telemetry disabled """
                os.environ["ANONYMIZED_TELEMETRY"] = "False"
                from vectordb.chroma_vector_store import ChromaVectorStore
                _ChromaVectorStore = ChromaVectorStore
            vector_store = _ChromaVectorStore(vector_db_config, embeddings)
        elif vector_type == "faiss":
            global _FaissVectorStore
            if _FaissVectorStore is None:
                from vectordb.faiss_vector_store import FaissVectorStore
                _FaissVectorStore = FaissVectorStore
            vector_store = _FaissVectorStore(vector_db_config, embeddings)
        elif vector_type == "opensearch":
            global _OpensearchVectorStore
            if _OpensearchVectorStore is None:
                from vectordb.opensearch_vector_store import OpensearchVectorStore
                _OpensearchVectorStore = OpensearchVectorStore
            vector_store = _OpensearchVectorStore(vector_db_config, embeddings)
        elif vector_type == "milvus":
            global _MilvusVectorStore
            if _MilvusVectorStore is None:
                from vectordb.milvus_vector_store import MilvusVectorStore
                _MilvusVectorStore = MilvusVectorStore
            vector_store = _MilvusVectorStore(vector_db_config, embeddings)

        if vector_store:
            return vector_store.get_vector_store_index(recreate_index)
        else:
            logger.error(f"Implementation class object missing for vector type {vector_type}")
            sys.exit(f"Implementation class object missing for vector type {vector_type}")
