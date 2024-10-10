import yaml
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredMarkdownLoader,
    UnstructuredFileLoader, PyPDFLoader
)
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import BedrockEmbeddings
import boto3
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core import config
import json
import os
import shutil
import sys
import logging
import tarfile
import zipfile


logger = logging.getLogger(__name__)
opensearch_indexes = []


class VectorConfig:
    def __init__(self, config):
        try:
            self.cnf = load_vectordb_configs(config)
            self.ai_applications = []
        except Exception as e:
            logger.error(f"Exception occurred while loading VectorDB configs {config}: {e}")
            sys.exit("Failed to load VectorDB configs")
        is_openai = False
        if "AI_applications" not in self.cnf:
            logger.error("AI_applications config does not exist in configuration file.")
            sys.exit("AI_applications config does not exist in configuration file.")
        if 'file_path' not in self.cnf["AI_applications"]:
            logger.error("AI_applications file path is not found in config, please provide valid file path")
            sys.exit("AI_applications file path is not found in config, please provide valid file path")
        ai_applications_file_path = self.cnf["AI_applications"]["file_path"]
        if not os.path.isfile(ai_applications_file_path):
            sys.exit("AI_applications file does not exist. File Path :- " + str(ai_applications_file_path))
        ai_applications_from_file = {}
        with open(ai_applications_file_path, 'r') as file:
            logger.info('Open AI_applications files :- ' + str(ai_applications_file_path))
            try:
                ai_applications_from_file = json.load(file)
            except Exception as e:
                logger.error("Error in loading AI_applications json file " + str(e))
                sys.exit("Error in loading AI_applications json file " + str(e))
            if ai_applications_from_file:
                ai_applications = [
                    ai_application['name'] for ai_application in ai_applications_from_file.get("AI_applications")
                    if ai_application.get("enable")
                ]
            else:
                logger.error(f"AI_applications config does not have any AI applications.")
                sys.exit("AI_applications config does not have any AI applications. "
                         "Please add AI applications in AI_applications json file")
            if ai_applications:
                for ai_application in ai_applications:
                    if ai_application in self.cnf["AI_applications"]:
                        ai_application_config = self.cnf["AI_applications"][ai_application]
                        check_index_path_and_data_path(ai_application_config)
                        if "implementation_class" in ai_application_config:
                            impl_class = ai_application_config.get("implementation_class")
                            if "OpenAIClient" in impl_class:
                                is_openai = True
                        else:
                            if "OpenAIClient" in self.cnf["AI_applications"]["default_implementation_class"]:
                                is_openai = True
                        self.ai_applications.append(ai_application)
                    else:
                        logger.error(f"{self.cnf['AI_applications']} does not have "
                                     f"configuration for {ai_application}")
                        sys.exit(f"{self.cnf['AI_applications']} does not have configuration for {ai_application}")
            else:
                logger.error(f"AI_applications config does not have any enable AI applications.")
                sys.exit("AI_applications config does not have any enable AI applications. "
                         "Please enable at least one AI application in AI_applications config")

        if is_openai:
            logger.info("OPENAI key is required for openai implementation")
            if 'OPENAI_API_KEY' not in os.environ or not os.getenv('OPENAI_API_KEY'):
                logger.info("OPENAI_API_KEY environment variable is not set.Read key from configuration file")
                if 'openai' not in self.cnf or 'key_file' not in self.cnf['openai']:
                    logger.error("OPENAI key file configuration is missing from configuration file.")
                    sys.exit("OPENAI_API_KEY is not set as environment variable.Trying to read to OPENAI key file but "
                             "OPENAI key file path is missing in configuration file")
                logger.info("Setting up openai api key")
                open_ai_key_file = self.cnf['openai']["key_file"]
                if open_ai_key_file:
                    logger.info(f"OPEN AI Key file={open_ai_key_file}")
                    if not os.path.exists(open_ai_key_file):
                        logger.error(f"OPEN AI Key file={open_ai_key_file} doesn't exists.")
                        sys.exit(f"OPEN AI Key file={open_ai_key_file} doesn't exists.\n"
                                 f"Please provide OPENAI key at mentioned path")
                    with open(open_ai_key_file, 'r') as file:
                        openai_key = file.read().strip()
                        os.environ['OPENAI_API_KEY'] = openai_key
                        logger.info(f"Set OPENAI_API_KEY environment variable with length= {str(len(openai_key))}")
                else:
                    logger.error(f"OPEN AI Key file={os.path.abspath(open_ai_key_file)} doesn't exists or not provided")
                    sys.exit(f"OPEN AI Key file={os.path.abspath(open_ai_key_file)} doesn't exists or not provided")


def check_index_path_and_data_path(ai_application_config):
    global opensearch_indexes
    if 'vectordb' not in ai_application_config:
        logger.error(f"VectorDB config does not exist in {ai_application_config}")
        sys.exit(f"VectorDB config does not exist in {ai_application_config}")
    if 'vector_type' not in ai_application_config['vectordb']:
        logger.error("Vector type is not found in config, please provide valid vector type")
        sys.exit("Vector type is not found in config, please provide valid vector type")
    if ai_application_config['vectordb']['vector_type'] == 'opensearch':
        if 'index_name' not in ai_application_config['vectordb']:
            logger.error(f"Index name is not found in config, please provide valid index name")
            sys.exit(f"Index name is not found in config, please provide valid index name")
        opensearch_indexes.append(ai_application_config['vectordb']['index_name'])
    elif ai_application_config['vectordb']['vector_type'] == 'milvus':
        if 'collection_name' not in ai_application_config['vectordb']:
            logger.error(f"Collection name is not found in config, please provide valid collection name")
            sys.exit(f"Collection name is not found in config, please provide valid collection name")
    elif 'index_path' not in ai_application_config['vectordb']:
        logger.error("Index path is not found in config, please provide valid index path")
        sys.exit("Index path is not found in config, please provide valid index path")
    if 'data_path' not in ai_application_config['vectordb']:
        logger.error("Data path is not found in config, please provide valid data path")
        sys.exit("Data path is not found in config, please provide valid data path")





def delete_extracted_directory(new_contents, data_path):
    for item in new_contents:
        path = os.path.join(data_path, item)
        if os.path.isfile(path):
            logger.info(f"Removing extracted {path} file from data path")
            os.remove(path)
        elif os.path.isdir(path):
            logger.info(f"Removing extracted {path} directory from data path")
            shutil.rmtree(path)


def get_all_files(folder_path):
    all_files = []
    for root, directories, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.tar'):
                with tarfile.open(file_path, 'r') as tar:
                    tar.extractall(path=root)
                    files = get_all_files(os.path.join(root, file.split('.')[0]))
                    all_files.extend(files)
            elif file.endswith('.zip'):
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(path=root)
                    files = get_all_files(os.path.join(root, file.split('.')[0]))
                    all_files.extend(files)
            elif file.endswith('.tgz'):
                with tarfile.open(file_path, 'r:gz') as tar:
                    tar.extractall(path=root)
                    files = get_all_files(os.path.join(root, file.split('.')[0]))
                    all_files.extend(files)
            else:
                file_tuple = (file, file_path)
                all_files.append(file_tuple)
            logger.info(f"Tuple of {file} and {file_path} added to all files list")
    logger.info(f"Collected all files from {folder_path}")
    return all_files


def check_valid_directory(directory):
    if os.path.isdir(directory):
        return True
    else:
        return False


def is_directory_empty(directory):
    # Check if directory exists
    if os.path.isdir(directory):
        # Get the list of files in the directory
        dir_contents = os.listdir(directory)
        # If the list is empty, return True
        if not dir_contents:
            return True
        else:
            return False
    else:
        return True


def get_loaders(files):
    loaders = []
    for file, file_path in files:
        # Create a loader for txt files
        if file.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
            loader_type = "TextLoader"
        # Create a loader for pdf files
        elif file.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            loader_type = "PyPDFLoader"
        # Markdown files
        elif file.endswith(".md"):
            loader = UnstructuredMarkdownLoader(file_path)
            loader_type = "UnstructuredMarkdownLoader"
        elif file.endswith(".json"):
            loader = TextLoader(file_path, encoding="utf-8")
            loader_type = "TextLoader"
        elif file.endswith(".jsonl"):
            loader = TextLoader(file_path, encoding="utf-8")
            loader_type = "TextLoader"
        else:
            loader = UnstructuredFileLoader(file_path)
            loader_type = "UnstructuredFileLoader"
        loaders.append(loader)
    return loaders


def create_documents(loaders):
    documents = []
    for loader in loaders:
        file_path = loader.file_path
        loader_class = loader.__class__.__name__
        documents.extend(loader.load())
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    )

    documents = text_splitter.split_documents(documents)
    return documents


def directory_clean_up(directory):
    if not is_directory_empty(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                logger.info(f"Removing {item_path} file in directory clean up activity")
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                logger.info(f"Removing {item_path} directory in directory clean up activity")
    logger.info(f"Directory cleanup activity done for {directory} directory")


def load_vectordb_configs(config_file_path):
    if isinstance(config_file_path, dict):
        return config_file_path
    elif isinstance(config_file_path, str):
        if os.path.isfile(config_file_path):
            file_extension = os.path.splitext(config_file_path)[-1].lower()
            if file_extension == '.json':
                with open(config_file_path, 'r') as file:
                    return json.load(file)
            elif file_extension == '.yaml' or file_extension == '.yml':
                with open(config_file_path, 'r') as file:
                    return yaml.safe_load(file)
            else:
                logger.info(f"VectorDB config file format is not supported, {config_file_path}")
                sys.exit("VectorDB config should either be a valid dict or a path to config file."
                         "Supported file formats are JSON and Yaml.")
        else:
            try:
                return json.loads(config_file_path)
            except ValueError:
                try:
                    return yaml.safe_load(config_file_path)
                except yaml.YAMLError:
                    logger.error(f"VectorDB config file format is not supported, {config_file_path}")
                    sys.exit("VectorDB config is an invalid JSON or YAML string")
    else:
        logger.error(f"VectorDB config file format is not supported, {config_file_path}")
        sys.exit("VectorDB config should either be a valid dict or a path to config file."
                 "Supported file formats are JSON and Yaml.")


def get_embedding_client(ai_application):
    implementation_class = config.Config["AI_applications"]["default_implementation_class"]
    ai_app_config = config.Config["AI_applications"][ai_application]
    if "implementation_class" in ai_app_config:
        implementation_class = ai_app_config.get("implementation_class")
    if "bedrock" in implementation_class.lower():
        return "bedrock"
    elif "openai" in implementation_class.lower():
        return "openai"
    else:
        logger.error(f"Embeddings not found for implementation class:: {implementation_class}")
        sys.exit(f"Embeddings not found for implementation class:: {implementation_class}, supported implementation "
                 "classes are\n  1. services.Bedrock_Application.BedrockClient.BedrockClient\n"
                 "  2. services.OpenAI_Application.OpenAIClient.OpenAIClient")


def get_bedrock_embeddings():
    if "bedrock" not in config.Config:
        logger.error("Bedrock configuration not found in configuration file")
        sys.exit("Bedrock configuration not found in configuration file. You have to provide bedrock "
                 "configuration in configuration file.")
    bedrock_config = config.Config["bedrock"]
    embedding_model = bedrock_config.get("embedding_model")
    llm_region = bedrock_config.get("region")
    bedrock_client = boto3.client("bedrock-runtime", region_name=llm_region)
    return BedrockEmbeddings(client=bedrock_client, model_id=embedding_model)


def get_langchain_embedding_client(embedding_client):
    match embedding_client:
        case "openai":
            return OpenAIEmbeddings()
        case "bedrock":
            return get_bedrock_embeddings()


def is_valid_data_path(data_path):
    if check_valid_directory(data_path):
        return True
    else:
        logger.error(f"Data path {data_path} is not a valid directory.")
        sys.exit(f"Data path {data_path} is not a valid directory. "
                 "Please provide valid data path in config")