# Vector Store Index Creation 

You can use this script to create Vector Store index for your data. This script will create index for your data and store it in the configured path.
You can run this script in a standalone mode which can also run as a separate process than the application server.
Currently this script supports only Chroma Vector Type.

## Contents
- [How to run with application server](#run-application-server)
- [How to run in standalone mode](#run-standalone-mode)

## How to run with application server <a name="run-application-server"></a>
1. User needs to provide configuration for vector db in config file of application server.
2. User needs to provide openai key file path in config file OR user can set it as environment variable.
3. User needs to provide index_path and data_path in config file.
4. User needs to provide vector_type as chroma in config file.
5. Secure chat will automatically create index for your data and store it in the configured path.


## How to run in standalone mode <a name="run-standalone-mode"></a>
1. Install dependencies run below command.
   ```bash
    pip install chromadb==0.4.13 click==8.1.7 langchain==0.0.310 openai==0.28.1 openai==0.28.1 urllib3==1.26.16
   ```
   _Note_ - Above dependencies will be installed automatically if same environment is used as of application server.

2. Create json file for multiple ai applications configuration and provide file_path under AI_Applications key in config file. 
   The all ai applications mentioned in AI_applications.json file must have configured under AI_Application key with same name in config file. 
   Please refer to the [sample configuration](../configs/default_config.yaml) for more details. 
   Please refer to the [sample ai application.json](../configs/AI_applications.json) for more details.
   
   _Note_ - In config we can add recreate_index true/false as vectordb config parameter to recreate index on every restart of vectordb standalone script.

3. Run below command to create Vector Store index(with default config file path)
    ```bash
    python vectordb_standalone.py
    ```
    _Note_ - Above command will use default config file path as configs/default_config.yaml.

4. OR run below command using your custom config file.
    ```bash
    python vectordb_standalone.py --config_path <confige file path>
    ```