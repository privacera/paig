import pytest
from unittest.mock import patch, MagicMock
from vectordb.faiss_vector_store import FaissVectorStore
from core import config

@pytest.fixture
def vector_store_instance():
    vector_db_config = config.Config['AI_applications']['sales_model']['vectordb']
    embeddings = MagicMock()
    return FaissVectorStore(vector_db_config, embeddings)

def test_create_vector_db_empty_data_path(vector_store_instance, tmpdir):
    vector_store_instance.data_path = str(tmpdir)
    with patch('vectordb.faiss_vector_store.get_all_files', return_value=[]), \
         patch('vectordb.faiss_vector_store.logger.info') as mock_logger_info, \
         patch('vectordb.faiss_vector_store.FAISS.from_texts') as mock_faiss_from_texts, \
         patch('vectordb.faiss_vector_store.FAISS.save_local') as mock_faiss_save_local:

        result = vector_store_instance.create_vector_db()

        assert result == mock_faiss_from_texts.return_value


def test_create_vector_db_non_empty_data_path(vector_store_instance, tmpdir):
    vector_store_instance.data_path = str(tmpdir)
    with patch('vectordb.faiss_vector_store.get_all_files', return_value=['file1', 'file2']), \
         patch('vectordb.faiss_vector_store.get_loaders') as mock_get_loaders, \
         patch('vectordb.faiss_vector_store.create_documents') as mock_create_documents, \
         patch('vectordb.faiss_vector_store.logger.info') as mock_logger_info, \
         patch('vectordb.faiss_vector_store.FAISS.from_documents') as mock_faiss_from_documents, \
         patch('vectordb.faiss_vector_store.FAISS.save_local') as mock_faiss_save_local:

        result = vector_store_instance.create_vector_db()

        assert result == mock_faiss_from_documents.return_value
        mock_get_loaders.assert_called_once_with(['file1', 'file2'])
        mock_create_documents.assert_called_once_with(mock_get_loaders.return_value)