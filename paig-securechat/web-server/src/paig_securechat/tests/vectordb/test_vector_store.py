from vectordb.faiss_vector_store import FaissVectorStore
from vectordb.chroma_vector_store import ChromaVectorStore
from vectordb.opensearch_vector_store import OpensearchVectorStore
from core import config
from core.utils import recursive_merge_dicts
import pytest


default_config = config.Config

@pytest.fixture
def mock_openai_api_key_file_path(tmpdir):
    file_path = tmpdir.join("test_openai_key.key")
    with open(file_path, "w") as file:
        file.write(" This is test open api key ")
    return str(file_path)


@pytest.fixture
def valid_index_path_directory(tmpdir):
    non_empty_dir = tmpdir.mkdir("chroma_index_path")
    return str(non_empty_dir)


@pytest.fixture
def valid_data_path_directory(tmpdir):
    non_empty_dir = tmpdir.mkdir("testdata")
    return str(non_empty_dir)


def test_faiss_vector_store(mocker, mock_openai_api_key_file_path, valid_index_path_directory, valid_data_path_directory):
    local_config_data = {"openai": {"key_file": mock_openai_api_key_file_path},
                         "AI_applications": {
                             "sales_model": {
                                 "vectordb": {
                                     "index_path": valid_index_path_directory,
                                     "data_path": valid_data_path_directory,
                                     "vector_type": "faiss"
                                 }
                             }
                         }
                    }
    config_data = recursive_merge_dicts(default_config, local_config_data)
    vector_db_config = config_data["AI_applications"]["sales_model"]["vectordb"]
    obj = FaissVectorStore(vector_db_config, "test_embeddings")
    mock_create_vector_db = mocker.patch('vectordb.faiss_vector_store.FaissVectorStore.create_vector_db',
                                         return_value=True)
    mock_get_vector_store_index = mocker.patch('vectordb.faiss_vector_store.FaissVectorStore.get_vector_store_index',
                                               return_value=True)

    assert obj.create_vector_db()
    assert obj.get_vector_store_index(False)
    mock_create_vector_db.assert_called_once()
    mock_get_vector_store_index.assert_called_once()


def test_chroma_vector_store(mocker, mock_openai_api_key_file_path, valid_index_path_directory, valid_data_path_directory):
    local_config_data = {"openai": {"key_file": mock_openai_api_key_file_path},
                         "AI_applications": {
                             "sales_model": {
                                 "vectordb": {
                                     "index_path": valid_index_path_directory,
                                     "data_path": valid_data_path_directory,
                                     "vector_type": "chroma"
                                 }
                             }
                         }
                    }
    config_data = recursive_merge_dicts(default_config, local_config_data)
    vector_db_config = config_data["AI_applications"]["sales_model"]["vectordb"]
    obj = ChromaVectorStore(vector_db_config, "test_embeddings")
    mock_create_vector_db = mocker.patch('vectordb.chroma_vector_store.ChromaVectorStore.create_vector_db', return_value=True)
    mock_get_vector_store_index = mocker.patch('vectordb.chroma_vector_store.ChromaVectorStore.get_vector_store_index',
                                               return_value=True)
    assert obj.create_vector_db()
    assert obj.get_vector_store_index(False)
    mock_create_vector_db.assert_called_once()
    mock_get_vector_store_index.assert_called_once()


def test_opensearch_vector_store(mocker, mock_openai_api_key_file_path, valid_index_path_directory,
                                 valid_data_path_directory):
    local_config_data = {"openai": {"key_file": mock_openai_api_key_file_path},
                         "AI_applications": {
                             "sales_model": {
                                 "vectordb": {
                                     "index_name": "test_index",
                                     "data_path": valid_data_path_directory,
                                     "vector_type": "opensearch"
                                 }
                             }
                         }
                         }
    config_data = recursive_merge_dicts(default_config, local_config_data)
    vector_db_config = config_data["AI_applications"]["sales_model"]["vectordb"]
    obj = OpensearchVectorStore(vector_db_config, "test_embeddings")
    mock_create_vector_db = mocker.patch('vectordb.opensearch_vector_store.OpensearchVectorStore.create_vector_db',
                                         return_value=True)
    mock_get_vector_store_index = mocker.patch(
        'vectordb.opensearch_vector_store.OpensearchVectorStore.get_vector_store_index',
        return_value=True
    )
    assert obj.create_vector_db()
    assert obj.get_vector_store_index(False)
    mock_create_vector_db.assert_called_once()
    mock_get_vector_store_index.assert_called_once()

