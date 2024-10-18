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
   3. To create a new application, go to `Application` > `AI Applications` and click the `CREATE APPLICATION` button on the right top. This will open a dialog box where you can enter the details of the application. 
   4. Once the application is created, Navigate to Application -> AI Applications and select the application you want to download the configuration file for. 
   5. Click on the `DOWNLOAD APP CONFIG` button from the right top to download the configuration file. 

8. Copy the downloaded configuration file to the `custom-configs/privacera-shield-config.json`.
   <br> Create `custom-configs` folder under `paig-securechat/web-server/src/paig_securechat` directory.
   ```bash
   mkdir -p custom-configs
   cp <path to privacera-shield-app-name-config.json> custom-configs/privacera-shield-config.json
   ```

9. Start PAIG SecureChat web server
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
   
10. Web server configuration can be found in the configs. Please refer to below [Configuration](#configuration) section for more details. 
11. In development mode, the swagger api server will be available at http://localhost:<_port_>/docs

### Steps to run the development web UI server
[How to use Secure Chat Web UI Server](../web-ui/README.md)


## Configuration <a name="configuration"></a>
Secure chat provides yaml based configuration. The configuration file is located at `configs`. 
Please refer to the [sample configuration](src/paig_securechat/configs/default_config.yaml) for more details.
More information about the configuration can be found in the [configuration](../README.md#configuration-a-nameconfigurationa) documentation.


## Logging <a name="logging"></a>
Secure chat provides way to configure logging configurations and level.
You can edit [logging configuration](src/paig_securechat/configs/logging.ini) to customize logging for secure chat.
