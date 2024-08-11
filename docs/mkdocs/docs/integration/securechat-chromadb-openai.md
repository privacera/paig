---
title: Privacera SecureChat With ChromaDB and OpenAI
---
# Privacera SecureChat With ChromaDB and OpenAI

This document provides a comprehensive guide to integrating Privacera SecureChat with ChromaDB and OpenAI. It includes detailed steps to tailor the integration to specific data sources and AI models.

## **Prerequisites**

Start with the instructions to setup the prerequisite for installing Privacera SecureChat. After you followed the below steps to install SecureChat, you can proceed
with the instructions in this document to configure and run your custom SecureChat.

1. [Docker Prerequisites](securechat.md#prerequisites)
2. [Setup Environment](securechat.md#setting-up-environment)
3. [PAIG Application Configuration](securechat.md#connecting-securechat-to-paig)
4. [Installing SecureChat](securechat.md#installing-securechat)

## **Installing Privacera SecureChat with ChromaDB and OpenAI**

### **OpenAI Key Configuration**

To use OpenAI, create a file named *openai.key* within the *custom-configs* folder and input your OpenAI key.

 ```shell
 echo "<<YOUR_OPEN_AI_KEY>>" > custom-configs/openai.key
 ```

### **Setting up Docker Compose**

Download the [docker-compose.yaml](snippets/securechat-openai-chromadb/docker-compose.yaml){:download="docker-compose.yaml"} file and save it in the `privacera_securechat` directory or the location from where you will be
running Privacera's SecureChat. This docker-compose file includes configurations for Privacera SecureChat and ChromaDB
setup. It also links the custom-configs folder to the SecureChat container and a data folder for loading embeddings into
ChromaDB.

```shell
mv ~/Downloads/docker-compose.yaml .
```

### **Sample Application**

!!! info "Default Application and Dataset"
    The sample AI_applications.json, config file and sales_data.tgz files are provided for demonstration purposes. You can use these
    files to try out first and then replace them with your own application and dataset.

Download the sample [AI_applications.json](snippets/securechat-openai-chromadb/AI_applications.json){:download="AI_applications.json"} configuration file and place it in 
the `custom-configs` folder. This file contains the UI configuration for the SecureChat application. The default
configuration includes a Sales Application with sample questions and messages.

```shell
mv ~/Downloads/AI_applications.json custom-configs/
```

Download the [openai_chromadb_config.yaml](snippets/securechat-openai-chromadb/openai_chromadb_config.yaml){:download="openai_chromadb_config.yaml"} file and place it to 
the `custom-configs` folder. This file contains the configuration for the ChromaDB and OpenAI integration. The
default configuration includes the Sales Application with paths to the data, AI application name, OpenAI configuration, 
and ChromaDB configuration.

```shell
mv ~/Downloads/openai_chromadb_config.yaml custom-configs/
```

Customize the `AI_applications.json` file to include your AI application name, description, messages, and sample questions. The structure of the `AI_applications.json` file is designed to be self-explanatory.

### **Sample Data**
To experiment with sample data initially, download the sample [sales_data.tgz](snippets/sales_data.tgz){:download="sales_data.tgz"} and extract it in the `data` folder.

```shell
tar -xvzf ~/Downloads/sales_data.tgz -C data
```

### **Running Privacera SecureChat**
Follow the [Running SecureChat](securechat.md#running-securechat) guide to start SecureChat and test the default Sales Application using examples
from the [Using SecureChat](securechat.html#using-securechat) section.

## **Customizing SecureChat for Your Application and Data**

To customize SecureChat for your use case, you need to get your data for embedding and AI application. You can follow 
the below steps to customize SecureChat for your application and data.

### **Creating new AI Application PAIG**

Create a new AI application in PAIG by following <!-- md:go_to_paig /#/ai_applications:Go To PAIG -->. After that
download the config file for the AI application and place it in the `custom-configs` folder.

### **Incorporating Your Data into SecureChat**

Add your data to SecureChat by placing it in sub-folder of `data`. E.g. `data/your_app_name`. You can have multiple
sub-folders for different sources of data. The data should be in the form of text files, PDF, etc. or any other format
that is supported by LangChain.

### **Customize GenAI Application**

The `custom-configs/AI_applications.json` file contains the UI configuration for the SecureChat application. You can 
customize the file to include your AI application name, description, messages, and sample questions. The structure of 
the `custom-configs/AI_applications.json` file is designed to be self-explanatory. Add your block of JSON to 
the `custom-configs/AI_applications.json` file.

```json
    {
      "name": "your_app_name",
      "display_name": "Your AppName",
      "description": "Your App Description",
      "enable": true,
      "default": true,
      "welcome_column1": {
        "header": "What this does?",
        "messages": [
          "Your App does this",
          "And your app does that"
        ]
      },
      "welcome_column2": {
        "header": "Sample questions...",
        "messages": [
          "Your app sample question 1",
          "Your app sample question 2"
        ]
      }
    }
```

### **Customize SecureChat**

Modify the `custom-configs/openai_chromadb_config.yaml` file to integrate your AI applications. You can clone
the existing section of `sales_data`. 

{{ read_csv('snippets/securechat-openai-chromadb/privacera_shield_configs.csv') }}


## **Running Privacera SecureChat with ChromaDB and OpenAI**

Follow the [Running SecureChat](securechat.md#running-securechat) guide to start SecureChat with ChromaDB and OpenAI integration.

## **Removing Default Sales Data**

Ensure SecureChat is configured for your AI application and data before removing the default Sales Application using the steps below:

1. Open the `custom-configs/AI_applications.json` file and delete the JSON block with `"name": "sales_data"`.
2. In the `custom-configs/openai_chromadb_config.yaml` file, remove the section labeled `sales_data:`.
3. Clear the `data/sales_data` folder's contents.
4. Restart SecureChat as described in [Running SecureChat](securechat.md#running-securechat).
5. Optionally, delete the `sales_data.tgz` file from the `data` folder.
