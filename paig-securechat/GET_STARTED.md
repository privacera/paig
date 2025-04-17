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
      
   2. Log into PAIG url: http://127.0.0.1:4545 using `admin/welcome1` as default username and password.
   3. To create a new application, go to `Application` > `AI Applications` and click the `CREATE APPLICATION` button on the right top. This will open a dialog box where you can enter the details of the application. 
   4. Once the Application is created, 
      - Navigate to `Paig Navigator` -> `AI Applications` and select the application for which you want to generate the api key. 
      - In the `API KEYS` tab, click the `GENERATE API KEY` button in the top-right corner to generate an API key. 
      - Provide a `Name` and `Description`, along with a `Expiry`, or select the `Max Validity (1 year)` checkbox to set default expiry.
      
        > **Note:** Once the API key is generated, it will not be shown again. Ensure you copy and securely store it immediately after generation.
   5. To initialize the PAIG Shield library in your AI application, export the __PAIG_APP_API_KEY__ as an environment variable.
        ```shell
        export PAIG_APP_API_KEY=<<AI_APPLICATION_API_KEY>>
        ``` 
      **OR**<br>
      Create a file called `paig.key` in the `custom-configs` folder and save the AI Application API key in the file.
        ```bash
        echo "<<AI_APPLICATION_API_KEY>>" > > custom-configs/paig.key
        ```
   
   6. Start the PAIG SecureChat web server

      ```bash
       python __main__.py run --host <host> --port <port> --debug True|False --config_path <path to config folder>
      ```
      One Such example is:
      ```bash
       python __main__.py run --host 0.0.0.0 --port 3535 --debug True --config_path configs
      ```
