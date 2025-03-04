# GET STARTED WITH PAIG SECURECHAT

## REQUIREMENTS

- **Python** >=3.10
- **NodeJS** >=18.18.0 
- **OS** : Linux/Debian based

# Fork and Clone the repository
1. Fork the repository from https://github.com/privacera/paig
2. Clone the repository if not already cloned.
   ```bash
   git clone git@github.com:<username>/paig.git
   ```

# Starting the Securechat Web Server

### Steps to run the development web Server
1. Create a virtual environment
    ```bash
    cd paig-securechat
    python -m venv venv
    ```
   OR
   ```bash
    cd paig-securechat
    python3 -m venv venv
    ```
2. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
3. Change directory to the web-server and Install the dependencies
    ```bash
    cd web-server
    pip install -r requirements.txt
    ```
6. Change directory to the src/paig_securechat
    ```bash
    cd src/paig_securechat
    ```
7. Create your own **OpenAI API** key and export it. Visit [this](https://platform.openai.com/) site to create the API key
   ```bash
   export OPENAIAPIKEY=<openai-api-key>
   ```
8. You can disable PAIG shield plugin by setting `--disable_paig_shield_plugin True` in the command line but we recommend to use PAIG Shield config for governance of the chatbot.
   ```bash
    python __main__.py run --disable_paig_shield_plugin True
   ```

9. Start PAIG SecureChat web server
   ```bash
    python __main__.py run
   ```

10. In development mode, the swagger api server will be available at http://localhost:<3535>/docs

# Starting Securechat Web-UI

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
4. Web UI configuration including proxy configuration can be found in package.json file. Proxy should be set to web server url.
    ```json
    "proxy": "http://localhost:3535"
    ```

5. Run the web UI
    ```bash
    npm start
    ```

# Using PAIG Shield config for governance of the chatbot (Optional)
   1. Start PAIG Server in `paig-server/backend/paig` by using the command below
      
        ```bash
      python __main__.py run --paig_deployment dev --config_path conf --host "127.0.0.1" --port 4545
        ```
        _Note:_ You need to have already set up [`paig-server`](../paig-server/GET_STARTED.md) for this command to work
      
   3. Log into PAIG url: http://127.0.0.1:4545 using `admin/welcome1` as default username and password.
   4. To create a new application, go to `Application` > `AI Applications` and click the `CREATE APPLICATION` button on the right top. This will open a dialog box where you can enter the details of the application. 
   5. Once the application is created, Navigate to Application -> AI Applications and select the application you want to download the configuration file for. 
   6. Click on the `DOWNLOAD APP CONFIG` button from the right top to download the configuration file.
   7. Copy the downloaded configuration file to the `custom-configs/privacera-shield-config.json`.<br>
      Create `custom-configs` folder under `paig-securechat/web-server/src/paig_securechat` directory.
      
      ```bash
      cd paig-securechat/web-server/src/paig_securechat
      mkdir -p custom-configs
      cp <path to privacera-shield-app-name-config.json> custom-configs/privacera-shield-config.json
      ```

   9. Start the PAIG SecureChat web server

      ```bash
       python __main__.py run --host <host> --port <port> --debug True|False --config_path <path to config folder>
      ```
      One Such example is:
      ```bash
       python __main__.py run --host 0.0.0.0 --port 3535 --debug True --config_path configs
      ```
