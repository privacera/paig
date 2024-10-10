import os.path
import zipfile
import tarfile
import pytest
from unittest.mock import MagicMock
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from vectordb.vector_utils import (
    is_directory_empty, get_all_files, get_loaders, create_documents, directory_clean_up, load_vectordb_configs,
    VectorConfig, delete_extracted_directory, check_valid_directory, get_bedrock_embeddings,
    get_langchain_embedding_client, check_index_path_and_data_path, is_valid_data_path
)
from core import config
from core.utils import recursive_merge_dicts

default_config = config.Config

@pytest.fixture
def empty_directory(tmpdir):
    empty_dir = tmpdir.mkdir("empty_dir")
    return empty_dir


@pytest.fixture
def non_empty_directory(tmpdir):
    non_empty_dir = tmpdir.mkdir("non_empty_dir")
    nested_non_empty_dir = non_empty_dir.mkdir("nested_non_empty_dir")
    non_empty_dir.join("test_file.txt").write("Test file added in directory")
    nested_non_empty_dir.join("test_file.txt").write("Test file added in nested directory")
    return non_empty_dir


@pytest.fixture
def data_files_directory(tmpdir):
    non_empty_dir = tmpdir.mkdir("non_empty_dir")
    non_empty_dir.join("txt_file.txt").write("This is txt_file")
    non_empty_dir.join("md_file.md").write("This is md_file")
    non_empty_dir.join("json_file.json").write("This is json_file")
    non_empty_dir.join("jsonl_file.jsonl").write("This is jsonl_file")
    non_empty_dir.join("pdf_file.pdf").write("This is pdf_file")
    non_empty_dir.join("docx_file.docx").write("This is pdf_file")
    return non_empty_dir


@pytest.fixture
def create_files(tmpdir):
    temp_dir = tmpdir.mkdir("files_dir")
    file1_path = temp_dir / "file1.txt"
    file2_path = temp_dir / "file2.txt"
    with open(file1_path, "w") as file:
        file.write("Test txt file for test data")

    with open(file2_path, "w") as file:
        file.write("Test txt file for test data")

    file3_path = temp_dir / "file3.txt"
    file4_path = temp_dir / "file4.txt"
    with open(file3_path, "w") as file:
        file.write("Test txt file for test data")

    with open(file4_path, "w") as file:
        file.write("Test txt file for test data")

    file5_path = temp_dir / "file5.txt"
    file6_path = temp_dir / "file6.txt"
    with open(file5_path, "w") as file:
        file.write("Test txt file for test data")

    with open(file6_path, "w") as file:
        file.write("Test txt file for test data")

    # Create a zip file and add the test files
    zip_file_path = temp_dir / "test_zip.zip"
    tar_file_path = temp_dir / "test_tar.tar"
    tgz_file_path = temp_dir / "test_tgz_files.tgz"
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        zipf.write(file1_path, "file1.txt")
        zipf.write(file2_path, "file2.txt")
    with tarfile.open(tar_file_path, 'w') as tar:
        tar.add(file3_path, "file3.txt")
        tar.add(file4_path, "file4.txt")
    with tarfile.open(tgz_file_path, 'w:gz') as tar:
        tar.add(file5_path, "file5.txt")
        tar.add(file6_path, "file6.txt")
    return temp_dir


@pytest.fixture
def valid_index_path_directory(tmpdir):
    non_empty_dir = tmpdir.mkdir("chroma_index_path")
    return non_empty_dir


@pytest.fixture
def valid_data_path_directory(tmpdir):
    non_empty_dir = tmpdir.mkdir("testdata")
    return non_empty_dir


@pytest.fixture
def temp_yaml_file(tmpdir):
    config_data = """
        vectordb:
            index_path: "/chroma_index_path"
            data_path: "/testdata"
            vector_type: "chroma"
        """
    file_path = tmpdir.join("vectordb_config.yaml")
    with open(file_path, "w") as file:
        file.write(config_data)
    return str(file_path)


@pytest.fixture
def temp_json_file(tmpdir):
    config_data = '{"index_path": "/chroma_index_path", "data_path":"/testdata", "vector_type":"chroma"}'
    file_path = tmpdir.join("vectordb_config.json")
    with open(file_path, "w") as file:
        file.write(config_data)
    return str(file_path)


@pytest.fixture
def temp_invalid_vector_config_file(tmpdir):
    file_path = tmpdir.join("vectordb_config.txt")
    with open(file_path, "w") as file:
        file.write("Test file for invalid vector json")
    return str(file_path)


@pytest.fixture
def mock_openai_api_key_file_path(tmpdir):
    file_path = tmpdir.join("test_openai_key.key")
    with open(file_path, "w") as file:
        file.write(" This is test open api key ")
    return str(file_path)


def test_is_directory_empty_valid_test(empty_directory):
    assert is_directory_empty(empty_directory)


def test_is_directory_empty_invalid_test(non_empty_directory):
    assert not is_directory_empty(non_empty_directory)


def test_get_all_files(create_files):
    result = get_all_files(create_files)
    assert len(result) == 6
    assert os.path.isdir(create_files)


def test_get_loaders(data_files_directory):
    files = get_all_files(data_files_directory)
    loaders = get_loaders(files)
    expected = TextLoader(files[0][1], encoding="utf-8")
    assert type(expected) == type(loaders[0])


def test_create_documents(non_empty_directory):
    files = get_all_files(non_empty_directory)
    loaders = get_loaders(files)
    documents = []
    for loader in loaders:
        documents.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )
    expected = text_splitter.split_documents(documents)
    result = create_documents(loaders)

    assert expected == result


def test_directory_clean_up(non_empty_directory):
    assert not is_directory_empty(non_empty_directory)
    directory_clean_up(non_empty_directory)
    assert is_directory_empty(non_empty_directory)


def test_load_vectordb_configs_dict():
    config_data = {"index_path": "/chroma_index_path", "data_path": "/testdata", "vector_type": "chroma"}
    result = load_vectordb_configs(config_data)
    assert result == config_data


def test_load_vectordb_configs_json_string():
    config_data = '{"index_path": "/chroma_index_path", "data_path": "/testdata", "vector_type": "chroma"}'
    expected = {"index_path": "/chroma_index_path", "data_path": "/testdata", "vector_type": "chroma"}
    result = load_vectordb_configs(config_data)
    assert result == expected


def test_load_vectordb_configs_yaml_string():
    config_data = """
        vectordb:
            index_path: "/chroma_index_path"
            data_path: "/testdata"
            vector_type: "chroma"
        """
    expected = {"vectordb": {"index_path": "/chroma_index_path", "data_path": "/testdata", "vector_type": "chroma"}}
    result = load_vectordb_configs(config_data)
    assert result == expected


def test_load_vectordb_configs_json_file(temp_json_file):
    expected = {"index_path": "/chroma_index_path", "data_path": "/testdata", "vector_type": "chroma"}
    result = load_vectordb_configs(temp_json_file)
    assert result == expected


def test_load_vectordb_configs_yaml_file(temp_yaml_file):
    expected = {"vectordb": {"index_path": "/chroma_index_path", "data_path": "/testdata", "vector_type": "chroma"}}
    result = load_vectordb_configs(temp_yaml_file)
    assert result == expected


def test_openai_api_key_set_as_environment_variable(mock_openai_api_key_file_path):
    local_config_data = {"openai": {"key_file": mock_openai_api_key_file_path}}
    config_data = recursive_merge_dicts(default_config, local_config_data)
    del os.environ['OPENAI_API_KEY']
    VectorConfig(config_data)
    assert os.getenv('OPENAI_API_KEY') == 'This is test open api key'
    del os.environ['OPENAI_API_KEY']


def test_load_vectordb_config_with_invalid_file_format():
    config_data = ["Invalid config file format"]
    with pytest.raises(SystemExit) as e:
        VectorConfig(config_data)
    assert ("VectorDB config should either be a valid dict or a path to config file.Supported file formats "
            "are JSON and Yaml.") == str(e.value)


def test_vector_config_without_openai_key(valid_index_path_directory, valid_data_path_directory):
    local_config_data = {
        "vectordb": {
            "index_path": valid_index_path_directory,
            "data_path": valid_data_path_directory,
            "vector_type": "chroma"
        }
    }
    config_data = recursive_merge_dicts(default_config, local_config_data)
    del config_data["openai"]
    with pytest.raises(SystemExit) as e:
        VectorConfig(config_data)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_vector_config_without_key_file_key(valid_index_path_directory, valid_data_path_directory):
    local_config_data = {
        "vectordb": {
            "index_path": valid_index_path_directory,
            "data_path": valid_data_path_directory,
            "vector_type": "chroma"
        }
    }
    config_data = recursive_merge_dicts(default_config, local_config_data)
    config_data['openai'] = {}
    with pytest.raises(SystemExit) as e:
        VectorConfig(config_data)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_vector_config_with_invalid_key_file_key(valid_index_path_directory, valid_data_path_directory):
    local_config_data = {
        "openai": {"key_file": ""},
        "vectordb": {
            "index_path": valid_index_path_directory,
            "data_path": valid_data_path_directory,
            "vector_type": "chroma"
        }
    }
    config_data = recursive_merge_dicts(default_config, local_config_data)
    with pytest.raises(SystemExit) as e:
        VectorConfig(config_data)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_vector_config_with_valid_key_file_key(valid_index_path_directory, valid_data_path_directory):
    local_config_data = {
        "openai": {"key_file": "Test OPENAI KEY file path"},
        "vectordb": {
            "index_path": valid_index_path_directory,
            "data_path": valid_data_path_directory,
            "vector_type": "chroma"
        }
    }
    config_data = recursive_merge_dicts(default_config, local_config_data)
    with pytest.raises(SystemExit) as e:
        VectorConfig(config_data)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_load_vectordb_configs_invalid_config_file(temp_invalid_vector_config_file):
    with pytest.raises(SystemExit) as e:
        VectorConfig(temp_invalid_vector_config_file)
    assert ("VectorDB config should either be a valid dict or a path to config file."
            "Supported file formats are JSON and Yaml.") == str(e.value)


def test_delete_extracted_directory(non_empty_directory):
    delete_extracted_directory({"test_file.txt", os.path.join(non_empty_directory, "nested_non_empty_dir")}, non_empty_directory)
    result = check_valid_directory(os.path.join(non_empty_directory,"test_file.txt"))
    assert not result


def test_load_vectordb_configs_invalid_config():
    config = "\n: invalid_json_and_yaml_config_str\n"
    with pytest.raises(SystemExit) as e:
        VectorConfig(config)
    assert "VectorDB config is an invalid JSON or YAML string" == str(e.value)


def test_config_without_ai_applications():
    config_data = {"openai": "This is test open api key"}
    with pytest.raises(SystemExit) as e:
        VectorConfig(config_data)
    assert "AI_applications config does not exist in configuration file." == str(e.value)


def test_invalid_ai_applications_config_file_path():
    config_data = {"AI_applications": {"file_path": "invalid_file_path"}}
    with pytest.raises(SystemExit) as e:
        VectorConfig(config_data)
    assert "AI_applications file does not exist. File Path :- invalid_file_path" == str(e.value)




@pytest.fixture
def config():
    # Define your config fixture data as needed
    return {
        "AI_applications": {
            "default_implementation_class": "default_impl_openai",
            "test_model": {"implementation_class": "bedrock"}
        },
        "bedrock": {"embedding_model": "amazon.test-embed-model-v1", "region": "us-west-2"}
    }


def test_get_bedrock_embeddings(monkeypatch):
    mock_boto3_client = MagicMock()
    monkeypatch.setattr("boto3.client", mock_boto3_client)
    mock_bedrock_embeddings = MagicMock()

    monkeypatch.setattr("vectordb.vector_utils.BedrockEmbeddings", mock_bedrock_embeddings)
    result = get_bedrock_embeddings()
    mock_boto3_client.assert_called_once_with("bedrock-runtime", region_name="us-west-2")
    mock_bedrock_embeddings.assert_called_once_with(client=mock_boto3_client.return_value,
                                                    model_id="amazon.titan-embed-text-v1")

    assert result == mock_bedrock_embeddings.return_value


def test_get_langchain_embedding_client_bedrock(monkeypatch):
    mock_get_bedrock_embeddings = MagicMock()
    monkeypatch.setattr("vectordb.vector_utils.get_bedrock_embeddings", mock_get_bedrock_embeddings)

    result = get_langchain_embedding_client('bedrock')
    mock_get_bedrock_embeddings.assert_called_once_with()

    assert result == mock_get_bedrock_embeddings.return_value


def test_get_langchain_embedding_client_openai(monkeypatch, config):
    config["AI_applications"]["test_model"]["implementation_class"] = "openai"
    mock_openai_embeddings = MagicMock()
    monkeypatch.setattr("vectordb.vector_utils.OpenAIEmbeddings", mock_openai_embeddings)
    result = get_langchain_embedding_client('openai')
    mock_openai_embeddings.assert_called_once()
    assert result == mock_openai_embeddings.return_value


def test_get_langchain_embedding_client_invalid_bedrock_config(config):
    bedrock = default_config["bedrock"]
    del default_config["bedrock"]
    config["AI_applications"]["test_model"]["implementation_class"] = "bedrock"
    with pytest.raises(SystemExit) as e:
        get_langchain_embedding_client("bedrock")
    default_config["bedrock"] = bedrock
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_check_index_path_and_data_path_missing_vectordb():
    ai_application_config = {}
    with pytest.raises(SystemExit) as e:
        check_index_path_and_data_path(ai_application_config)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_check_index_path_and_data_path_missing_vector_type():
    ai_application_config = {'vectordb': {}}
    with pytest.raises(SystemExit) as e:
        check_index_path_and_data_path(ai_application_config)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_check_index_path_and_data_path_missing_opensearch_index_name():
    ai_application_config = {
        'vectordb': {
            'vector_type': 'opensearch'
        }
    }
    with pytest.raises(SystemExit) as e:
        check_index_path_and_data_path(ai_application_config)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_check_index_path_and_data_path_missing_index_path():
    ai_application_config = {
        'vectordb': {
            'vector_type': 'chroma'
        }
    }
    with pytest.raises(SystemExit) as e:
        check_index_path_and_data_path(ai_application_config)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_check_index_path_and_data_path_missing_data_path(valid_index_path_directory):
    ai_application_config = {
        'vectordb': {
            'vector_type': 'chroma',
            'index_path': valid_index_path_directory
        }
    }
    with pytest.raises(SystemExit) as e:
        check_index_path_and_data_path(ai_application_config)
    assert e.type == SystemExit
    assert len(str(e.value)) != 0


def test_valid_index_path(valid_index_path_directory):
    result = check_valid_directory(valid_index_path_directory)
    assert result


def test_check_invalid_index_path():
    result = check_valid_directory("invalid/index/path")
    assert not result


def test_check_is_valid_data_path(valid_data_path_directory):
    result = is_valid_data_path(valid_data_path_directory)
    assert result


def test_check_invalid_data_path(empty_directory):
    with pytest.raises(SystemExit) as e:
        is_valid_data_path("invalid/data/path")
    assert e.type == SystemExit
    assert len(str(e.value)) != 0
