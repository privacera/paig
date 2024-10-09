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
1. Clone the repository
2. Change directory to the web-server repository
3. Create a virtual environment
    ```bash
    python -m venv venv
    ```
4. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
5. Install the dependencies
    ```bash
    pip install -r requirements.txt
    ```
6. Change directory to the src/paig_securechat
    ```bash
    cd src/paig_securechat
    ```
7. Run the web server
   ```bash
    python main.py --secure_chat_deployment dev|prod --debug True|False --config_path <path to config folder>
    
   ```
   One Such example is:
   ```bash
    python main.py --secure_chat_deployment dev --debug True --config_path configs
    
   ```
8. Web server configuration can be found in the configs. Please refer to [Configuration](#configuration) section for more details.
9. In development mode, the swagger api server will be available at http://localhost:<_port_>/docs


## Configuration <a name="configuration"></a>
Secure chat provides yaml based configuration. The configuration file is located at `configs`. 
Please refer to the [sample configuration](src/paig_securechat/configs/default_config.yaml) for more details.
More information about the configuration can be found in the [configuration](../README.md) documentation.

## Logging <a name="logging"></a>
Secure chat provides way to configure logging configurations and level.
You can edit [logging configuration](src/paig_securechat/configs/logging.ini) to customize logging for secure chat.
