# PAIG SecureChat Docker

Secure Chat provides a docker based deployment of the Secure Chat application. 
With minimal configuration, you can deploy Secure Chat in your environment.

## Contents
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Configure Docker Compose File](#configuration-docker-compose)
- [Docker compose with Opensearch](#docker-compose-with-opensearch)
- [Docker compose with Milvus](#docker-compose-with-milvus)
- [Steps to run the docker(With Docker Compose File)](#steps-to-run-the-docker)
- [Steps to run the docker(Without Docker Compose File)](#steps-to-run-the-docker-without)


## Prerequisites <a name="prerequisites"></a>
Docker is required to run the Secure Chat docker.

## Configuration <a name="configuration"></a> 
Secure Chat provides a way to configure the application using configuration file.Optimum configuration required to run the application is provided in the default configuration file.
Although you can provide your own configuration file to override the default configuration.
Please refer to [Secure Chat Configurations](../README.md) for more details.

1. You can provide the configuration in the configs folder. 
   You can reuse the default configuration provided in configuration file with your custom configurations.

   default => default_config.yaml <br />
   custom => <ENVIRONMENT_NAME>_config.yaml<br />
   default environment => dev<br />
   You can pass environment through the docker-compose file or through docker run command.
2. **Database** setup/upgrade will be taken care by the docker. 
   You just need to provide the database connection string in the configuration file.
   One such example is:
   ```yaml
   database:
       url: "sqlite+aiosqlite:////paig_securechat/test.db"
   
   ```
   Format should be as follows:
   ```yaml
   dialect+driver://username:password@host:port/database
   ```
   _Note_ - Secure chat uses **Async** SQLAlchemy to connect to the database.
   For more information on database setup please refer to [Secure Chat Database](../web-server/src/paig_securechat/database_setup/README.md)
3. If you have opted to use OpenAI , Please provide OpenAI Key file path in configuration which should be accessible from docker OR 
   you have to pass it as environment variable in docker-compose file or in the docker run command.

_Note_: If you are running `PAIG` locally outside of a Docker container, 
update the `shieldServerUrl` in the downloaded AI app configuration to `http://host.docker.internal:4545`.


## Configure Docker Compose File <a name="configuration-docker-compose"></a> 
Secure Chat provides a way to configure the application and docker-compose file.
To configure docker, you need to provide the following details in the docker-compose file:

1. You can provide volumes in the docker-compose file. 
   You can mount the volumes to the host machine. 
   This will allow you to persist the data even if the docker is stopped.
   All you need to do is provide the path to the local directory in the docker-compose file.
   ```yaml
   volumes:
      - ${PWD}/custom-configs:/workdir/custom-configs
      - ${PWD}/securechat/logs:/workdir/securechat/logs
      - ${PWD}/securechat/sales/data:/workdir/securechat/sales/data
      - ${PWD}/securechat/sales/index:/workdir/securechat/sales/index
      - ${PWD}/securechat/db:/workdir/securechat/db
   ```
    _Note_ - Above volumes configuration is optional. You can opt to provide all volumes or only few volumes.


2. You can pass environment through the docker-compose file.
   ```yaml
   command:
      - -e dev
   ```
   _Note_ - Config folder will be used which is configured in the docker-compose file in step #1.
   If you have not configured the config folder in the docker compose file , configs folder inside _web-server/src/paig_securechat/configs_ will be used. 

3. If using OPEN AI model then only configure OPENAI_API_KEY using below different ways. 
   1. Pass the environment variable while running docker image, like below example.
      ```bash
      docker run -p <port>:<port> --name paig-securechat --env OPENAI_API_KEY=<insert your key here> <built image name>
      ```
   2. Using Docker Compose File , please add following environment variable in the docker-compose file .
      ```yaml
      environment:
         OPENAI_API_KEY: "<INSERT YOU KEY HERE>"
       ```
   3. The user can use the OpenAI proxy endpoint. To set a custom base URL for OpenAI API requests, the user must configure the OPENAI_API_BASE environment variable with the desired proxy endpoint.
      ```yaml
      environment:
         OPENAI_API_BASE: "<INSERT YOU BASE URL HERE>"
      ```
   4. Using openai.key file, Provide the OPENAI_API_KEY by adding openai.key file in custom-configs folder.

   5. Run the docker-compose file
      ```bash
      docker-compose up
      ```
       _Note_- You can also run the docker-compose file in detached mode.
       ```bash
       docker-compose up -d
       ```
      * You might run into permission denied issue for mounted volumes mentioned in docker-compose file.
   
      _Error looks like_:
      ```bash
       Error response from daemon: error while creating mount source path '<${PWD}>/securechat/logs': chown '<${PWD}>/securechat/logs' permission denied
      ```
      OR
      ```bash
      /workdir/start_securechat.sh: line 54: securechat/logs/db_setup.log: Permission denied
      ```
      **Solution**:- Please create directories mentioned as mounted volumes manually. Created directories should have read-write permissions.

      (i) Create folders using below commands:
      ```bash
      mkdir -p securechat/logs
      mkdir -p securechat/db
      mkdir -p securechat/sales/data
      mkdir -p securechat/sales/index
      ```
      (ii) Change permissions using below command:
      ```bash
      chmod -R 776 securechat/logs
      chmod -R 776 securechat/db
      chmod -R 776 securechat/sales/data
      chmod -R 776 securechat/sales/index
      ```


## Docker compose with Opensearch
   Secure Chat provides a way to configure the application and docker-compose file with opensearch. 
   Do following steps to run Secure Chat with Opensearch:
   1. Set dev_openai_opensearch as environment for SECURE_CHAT_DEPLOYMENT in docker-compose file.
   2. Provide your opensearch configurations in dev_openai_opensearch_config.yaml under custom-configs.You can refer to [sample-opensearch-config](sample-custom-configs/dev_openai_opensearch_config.yaml)
    
   _Note_: You can refer to [Sample-docker-compose-opensearch](docker-compose-with-local-opensearch.yml).
   
## Docker compose with Milvus
   Secure Chat provides a way to configure the application and docker-compose file with milvus. 
   Do following steps to run Secure Chat with Milvus:
   1. Set dev_openai_milvus as environment for SECURE_CHAT_DEPLOYMENT in docker-compose file.
   2. Provide your milvus configurations in dev_openai_milvus_config.yaml under custom-configs. You can refer to [sample-milvus-config](sample-custom-configs/dev_openai_milvus_config.yaml)

   _Note_: You can refer to [Sample-docker-compose-milvus](docker-compose-with-local-milvus.yml).


## Steps to run the docker(With Docker Compose File) <a name="steps-to-run-the-docker"></a>

1. Build the docker image
   ```bash
   ./build_image.sh
   ```
2. Configure the docker-compose file as per your requirement
3. Run the docker
   ```bash
   ./run_docker.sh
   ```
   
4. Once the docker is up and running, you can access the web application at http://localhost:3636 (your configured nginx port)


## Steps to run the docker(Without Docker Compose File) <a name="steps-to-run-the-docker-without"></a>
1. Build the docker image
   ```bash
   ./build_image.sh
   ```

2. Run the docker run command
    ```bash
   docker run -p <port>:<port> --name paig-securechat --env OPENAI_API_KEY=<insert your key here> <built image name>
   
   # with volume mounts for logs and database
   docker run -p <port>:<port> --name paig-securechat --env OPENAI_API_KEY=<insert your key here> -v ./logs:/workdir/securechat/logs -v ./db:/workdir/securechat/db <built image name>

   ```
   One such example is :-
   ```bash
   docker run -p 3636:3636 --name paig-securechat --env OPENAI_API_KEY='xxxxx' paig-securechat:latest
   
   # with volume mounts for logs and database
   docker run -p 3636:3636 --name paig-securechat --env OPENAI_API_KEY='xxxxx' -v ./logs:/workdir/securechat/logs -v ./db:/workdir/securechat/db privacera/paig-securechat:latest

   ```
   
   _Note_- You can also map volumes to the host machine, provide other command line arguments as per docker compose file configuration in above command as well. 
   
3. Once the docker is up and running, you can access the web application at http://localhost:3636 (your configured nginx port)
