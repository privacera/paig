# PAIG SecureChat

Secure Chat is a conversational AI chat bot .
Secure chat allows users to create  conversations with an AI chat bot which can optionally  be governed by PAIG. 
Secure chat SDK provides an easy to use, plugable platform which will allow developers/users to have open source chat bot SDK.

## Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Configuration](#configuration)
- [How to Start Development Server](web-server/README.md#how-to-start-development-server-a-namedevelopmentservera)
- [PAIG SecureChat as a Python library](web-server/src/README.md)
- [How to Setup Database](#databsesetup)
- [How to Create Vector Embeddings](#vector-embeddings)
- [How to Deploy Using Docker](docker/README.md)
- [Docker compose with Opensearch](docker/README.md#docker-compose-with-opensearch)
- [Docker compose with Milvus](docker/README.md#docker-compose-with-milvus)
- [Generate hashed password](#hashedpassword)

## Overview <a name="overview"></a>
Secure Chat SDK is a pluggable platform which allows you to add more features to your chat bot as you go along.
You can use ready to use Secure Chat application or you can use Secure Chat SDK to create your own chat bot.
1. **Secure Chat Docker Mode:** You can simply use pre-built Secure Chat dockers and deploy it in your environment with bare minimum configurations.
   Please refer to <a name="dockerserver">How to Deploy Using Docker</a> for more details.
2. **Secure Chat Development Mode:** You can use Secure Chat SDK to create your own chat bot. Secure Chat SDK is a pluggable platform which allows you to add more features to your chat bot as you go along.
    Please refer to <a name="developmentserver">How to Start Development Server</a> for more details.
3.  **Secure Chat as a Python library:** Please refer to [PAIG SecureChat as a Python library](web-server/src/README.md)
## Technology Stack <a name="technology-stack"></a>
Secure chat is a web based application. It uses the following technologies:
* **Web Application Framework:** ReactJS
* **Backend:** FastAPI (Python)
* **Database:** Configured by the user
* **AI:**  Configured by the user

## Configuration <a name="configuration"></a>
Secure Chat provides overlay configuration. When you run Secure Chat as python package or in development mode(SDK) will use the default configuration provided in the `standalone_config.yaml` file.
This default configuration can be overridden by the user provided custom configuration.
<br>User can provide the custom configuration in the following ways:
1. Create a `custom-configs` folder.
   ```bash
    mkdir -p custom-configs
   ```
2. Create `standalone_config.yaml` configuration file under `custom-configs` folder to override default configuration.
3. In custom configuration file , user should provide new configuration key-values or override the existing configuration.
4. To override the existing configuration, user should provide the same key in the `standalone_config.yaml` configuration file as it is in configuration with same structure.
    For example:
    ```yaml
    database:
        url: "sqlite+aiosqlite:////paig_securechat/test.db"
        type: "sqlite"
    ```
    If user wants to override the database url, user should provide the same key in the custom configuration file as it is in configuration with same structure.
    ```yaml
    database:
      url: "sqlite+aiosqlite:////new.db"
   ```
### Okta Authorization Configuration
1. To enable Okta Authorization, user should provide the below configuration in the custom configuration file.
   ```yaml
   security:
       okta:
          enabled: "true"
          issuer: "OKTA_ISSUER"
          audience: "api://default"
          client_id: "OKTA_CLIENT_ID"
   ```
### Basic Authorization Configuration
1. To enable Basic Authorization, user should provide the below configuration in the custom configuration file.
   In which `user_secrets.csv` file should have first column name as `Username` and second column as `Secrets`. 
   Add usernames and hashed passwords in the `user_secrets.csv` file. Generate hashed `Secrets`(password) using [Generate hashed password](#hashedpassword) section.
   <br> The default `user_secrets.csv` file with default usernames and secrets is provided in the [configs](web-server/src/paig_securechat/configs/user_secrets.csv) folder.
   ```yaml
   security:
       basic_auth:
           enabled: "true"
           credentials_path: "configs/user_secrets.csv"
   ```
   _Note_:- 
   1. In default `user_secrets.csv` file the password for all users is `welcome1`
   2. To override default basic auth secrets, update the `credentials_path` with your own custom `cvs` file path.
       
### Secure Chat with OPENAI configuration
1. In custom configuration file user should provide new configuration key-values to override the existing configuration._
    ```yaml
    openai:
        key_file: "<openai.key file path>"
    AI_applications:
        file_path: "<AI_applications.json file path>"
        <ai_application_name>:
           implementation_class: "services.OpenAI_Application.OpenAIClient.OpenAIClient"
   ```
   _Note_:- 
   1. ai_application_name is the name of the application which is configured in the AI_applications.json file [sample configuration](web-server/src/paig_securechat/configs/AI_applications.json).
   2. User can set up OPENAI_API_KEY in different ways(Refer Configure Docker Compose File in [Secure Chat Docker](docker/README.md))
   3. The user can use the OpenAI proxy endpoint. To set a custom base URL for OpenAI API requests, the user must configure the OPENAI_API_BASE environment variable with the desired proxy endpoint.

### Secure Chat with Bedrock configuration
1. In custom configuration file ,user should provide new configuration key-values to override the existing configuration.
    ```yaml
    bedrock:
        model: "<aws model>"
        region: "<aws region>"
    AI_applications:
        file_path: "<AI_applications.json file path>"
        <ai_application_name>:
           implementation_class: "services.Bedrock_Application.BedrockClient.BedrockClient"
   ```
   _Note_:- ai_application_name is the name of the application which is configured in the AI_applications.json file [sample configuration](web-server/src/paig_securechat/configs/AI_applications.json).

## How to Start Development Server <a name="developmentserver"></a>


### Prerequisites
* **NodeJS:** >=18.18.0
* **Python:** >=3.9.6

### Steps to run the development web server
[How to use Secure Chat Web Server](web-server/README.md)

### Steps to run the development web UI server
[How to use Secure Chat Web UI Server](web-ui/README.md)

## How to Setup Database <a name="databsesetup"></a>
Secure Chat allows user to configure database of their choice in the configuration file.
Secure Chat uses SQLAlchemy to connect to the database. Secure Chat Docker Mode will automatically create/update the tables in the database.
Whereas in Secure Chat Development Mode, user will have to create/update the tables in the database manually.
Please refer to [Secure Chat Database](web-server/src/paig_securechat/database_setup/README.md) for more details.

## How to Create Vector Embeddings <a name="vector-embeddings"></a>
Secure Chat will automatically create vector embeddings for the questions and answers in the configured path. 
Whereas secure chat also provide ways to create vector embeddings for the questions and answers manually using standalone mode.
Please refer to [Secure Chat Vector Embeddings](web-server/src/paig_securechat/vectordb/README.md) for more details.

## How to Deploy Using Docker <a name="dockerserver"></a>
Secure Chat can be deployed using docker. Please refer to [Secure Chat Docker](docker/README.md) for more details.


## How to generate hashed password <a name="hashedpassword"></a>
You can generate hashed password using two ways:
1. **Run standalone python script to generate hashed password**
   i. Create virtual environment and install the dependencies.
   ```bash
    python -m venv venv
    source venv/bin/activate
    pip install werkzeug
    ```
   i. Change directory to the workdir directory.
   ```bash
    cd scripts
    ```
   ii. Run the standalone_hash_password_create.py script.
   ```bash
    python standalone_hash_password_create.py
    ```
   One such example is :-
   ```bash
    python standalone_hash_password_create.py
    Enter password: admin123
    Hashed password: scrypt:32768:8:1$GHQiQsp0WgxvyQTZ$258154388558ffad80928cd0434168356d4789da6cbdfac7772ebba6bd996d23bc6fd2460f81472ae1ec4d76097f947afa77405c6b5aaaeafc64fa5c38e77feb
    ```
   [Standalone Hash Password Script](scripts/standalone_hash_password_create.py)

2. **Follow below steps to generate hashed password.**
   
   i. Install Werkzeug python library.
   ```bash
    pip install Werkzeug
    ```
    ii. Run this python snippet with your new password.
    ```bash
   from werkzeug.security import generate_password_hash
   print(generate_password_hash("<put your password here>", "sha256"))
      ```