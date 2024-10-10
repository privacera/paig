import pytest
from unittest.mock import patch, MagicMock
from vectordb.milvus_vector_store import MilvusVectorStore
from core import config


@pytest.fixture
def vector_store_instance():
    vector_db_config = config.Config['AI_applications']['sales_model']['vectordb']
    vector_db_config['collection_name'] = 'test_collection'
    embeddings = MagicMock()
    return MilvusVectorStore(vector_db_config, embeddings)


def test_create_vector_db_empty_data_path(vector_store_instance, tmpdir):
    vector_store_instance.data_path = str(tmpdir)
    with patch('vectordb.milvus_vector_store.get_all_files', return_value=[]), \
         patch('vectordb.milvus_vector_store.logger.info') as mock_logger_info, \
         patch('vectordb.milvus_vector_store.Milvus.from_documents') as mock_milvus_from_texts:

        vector_store_instance.create_vector_db()

        assert vector_store_instance.vector_store is None



def test_create_vector_db_non_empty_data_path(vector_store_instance, tmpdir):
    vector_store_instance.data_path = str(tmpdir)
    with patch('vectordb.milvus_vector_store.get_all_files', return_value=['file1', 'file2']), \
         patch('vectordb.milvus_vector_store.get_loaders') as mock_get_loaders, \
         patch('vectordb.milvus_vector_store.create_documents') as mock_create_documents, \
         patch('vectordb.milvus_vector_store.MilvusVectorStore.chunk_list',
               return_value=mock_create_documents.return_value) as mock_milvus_chunk_list, \
         patch('vectordb.milvus_vector_store.Milvus.from_documents') as mock_milvus_from_documents:

        vector_store_instance.create_vector_db()

        assert vector_store_instance.vector_store is None
        mock_milvus_chunk_list.assert_called_once_with(mock_create_documents.return_value, 500)
        mock_get_loaders.assert_called_once_with(['file1', 'file2'])
        mock_create_documents.assert_called_once_with(mock_get_loaders.return_value)
