# GET STARTED WITH PAIG SECURECHAT

## REQUIREMENTS

- **Python** >=3.10
- **NodeJS** >=18.18.0 
- **OS** : Linux/Debian based


## CONTENTS
- [Starting Securechat Web Server](#starting-the-securechat-web-server)
- [Starting Securechat Web-UI](#starting-securechat-web-ui)

# Clone the repository
1. Fork the repository from https://github.com/privacera/paig
2. Clone the repository if not already cloned.
   ```bash
   git clone git@github.com:<username>/paig.git
   ```

# Starting the Securechat Web Server

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
   1. Start PAIG Server in `paig-server/backend/paig` by using the command below
   
        ```bash
      python __main__.py run --paig_deployment dev --config_path conf --host "127.0.0.1" --port 4545
        ```
        _Note:_ You need to have already set up [`paig-server`](../paig-server/GET_STARTED.md) for this command to work 

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

9. Change the model from gpt-4o to one of the available models in the .yaml configuration files in `paig-securechat/web-server/src/paig_securechat/configs`.
    ```
    model: "gpt-4o-mini"
    ```

10. Create your own **OpenAI API** key. Visit [this](https://platform.openai.com/) site to create the API key

11. Start PAIG SecureChat web server
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

## Starting Securechat Web-UI

### Steps to run the development web UI
1. Change directory to the web-ui repository
2. Install the dependencies
    ```bash
    npm install
    ```
   _Note_ - If you get `Conflicting peer dependency` error after running above `npm install` command, Try below command.
    ```bash
    npm install --legacy-peer-deps
    ```
3. Web UI configuration including proxy configuration can be found in package.json file. Proxy should be set to web server url.
    ```json
    "proxy": "http://localhost:3535"
    ```
   _Note_ - If `http://localhost:3535` not working for you, try `http://127.0.0.1:3535` or `http://<host_ip>:3535`
4. Run the web UI
    ```bash
    npm start
    ```