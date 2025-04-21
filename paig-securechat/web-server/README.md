# PAIG Securechat Web Server

Secure Chat provides a web interface to interact with the chat bot. It is a ReactJS based web application.

## Contents
- [How to Start Development Server](#developmentserver)
- [Configuration](#configuration)
- [Logging](#logging)

## How to Start Development Server <a name="developmentserver"></a>
### Prerequisites
* **Python:** >=3.9.6

### Steps to run the development web Server
1. You will need your own copy of paig to work on the code. 
<br>Go to the [PAIG GitHub](https://github.com/privacera/paig) page and hit the Fork button. Clone your fork to your machine.
   ```bash
   git clone git@github.com:<username>/paig.git
   cd paig
   ```
2. Change directory to the paig-securechat repository.
    ```bash
    cd paig-securechat
    ```
3. Create a virtual environment
    ```bash
    python -m venv venv
    ```
   OR
   ```bash
    python3 -m venv venv
    ```
4. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
5. Change directory to the web-server and Install the dependencies
    ```bash
    cd web-server
    pip install -r requirements.txt
    ```
6. Change directory to the src/paig_securechat
    ```bash
    cd src/paig_securechat
    ```
7. We recommend to use PAIG Shield config for governance of the chatbot. 
   1. Start PAIG as python package. PAIG is a python library which can be installed using pip.
      ```bash
      pip install paig-server
      python -m spacy download en_core_web_lg
      ```
      You can simply run the PAIG as a service by running following command:
        ```bash
        paig run
        ```
   2. Log into PAIG url: http://127.0.0.1:4545 using `admin/welcome1` as default username and password.
   3. To create a new application, go to `Paig Navigator` > `AI Applications` and click the `CREATE APPLICATION` button on the right top. This will open a dialog box where you can enter the details of the application. 
   4. Once the Application is created, 
         1. Navigate to **Paig Navigator** -> **AI Applications** and select the application for which you want to generate the api key. 
         2. In the **API KEYS** tab, click the **GENERATE API KEY** button in the top-right corner to generate an API key. 
         3. Provide a **Name** and **Description**, along with a **Expiry**, or select the **Max Validity (1 year)** checkbox to set default expiry.
         __Note__:- Once the API Key is generated, it will not be displayed again. Ensure you copy and securely store it immediately after generation.
   5. To initialize the PAIG Shield library in your AI application, export the __PAIG_APP_API_KEY__ as an environment variable.
        ```shell
        export PAIG_APP_API_KEY=<<AI_APPLICATION_API_KEY>>
        ``` 
      **OR**<br>
      Create a file called `paig.key` in the `custom-configs` folder and save the AI Application API key in the file.
        ```bash
        mkdir -p custom-configs
        echo "<<AI_APPLICATION_API_KEY>>" > custom-configs/paig.key
        ``` 

8. Start PAIG SecureChat web server
   ```bash
    python __main__.py run --host <host> --port <port> --debug True|False --config_path <path to config folder> --openai_api_key <openai api key>
   ```
   One Such example is:
   ```bash
    python __main__.py run --host 0.0.0.0 --port 3535 --debug True --config_path configs --openai_api_key <openai api key>
   ```
   _Note:_ You can disable PAIG shield plugin by setting `--disable_paig_shield_plugin True` in the command line.
   ```bash
    python __main__.py run --disable_paig_shield_plugin True
   ```
   
9. Web server configuration can be found in the configs. Please refer to below [Configuration](#configuration) section for more details. 
10. In development mode, the swagger api server will be available at http://localhost:<_port_>/docs

### Steps to run the development web UI server
[How to use Secure Chat Web UI Server](../web-ui/README.md)


## Configuration <a name="configuration"></a>
Secure chat provides yaml based configuration. The configuration file is located at `configs`. 
Please refer to the [sample configuration](src/paig_securechat/configs/default_config.yaml) for more details.
More information about the configuration can be found in the [configuration](../README.md#configuration-a-nameconfigurationa) documentation.


## Logging <a name="logging"></a>
Secure chat provides way to configure logging configurations and level.
You can edit [logging configuration](src/paig_securechat/configs/logging.ini) to customize logging for secure chat.
