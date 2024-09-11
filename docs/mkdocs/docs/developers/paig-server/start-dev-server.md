## Technology Stack <a name="technology-stack"></a>
PAIG provides a platform for AI governance. It allows users to governance and audits the data on one platform. 
PAIG uses the following technologies:<br/>
* **Web Application Framework:** ReactJS<br/>
* **Backend:** FastAPI (Python)<br/>
* **Database:** Relational Database like SQLite, MySQL, PostgreSQL etc (default sqlite)<br/>


## How to Start Web Server <a name="developmentserver"></a>
### Prerequisites
* **Python:** >=3.10
* **NodeJS:** =14.17.5

### Steps to run the development Web Server
1. Fork the repository https://github.com/privacera/paig.
   ```bash
   git clone https://github.com/YOUR_USERNAME/paig.git
   ```
2. Run the script to build the web UI.
   ```bash
   cd scripts
   source ./build_ui.sh
   ```
3. Change directory to the root level of the repository.
4. Go to the backend directory.
   ```bash
    cd backend
    ```
5. Create a virtual environment.
    ```bash
    python3 -m venv venv
    ```
6. Activate the virtual environment.
    ```bash
    source venv/bin/activate
    ```
7. Install the dependencies.
    ```bash
    pip install -r requirements.txt
    ```
8. Change directory to the paig.
    ```bash
    cd paig
    ```
9. Run the web server.
   ```bash
   python __main__.py run --paig_deployment dev|prod --config_path <path to config folder> --host <host_ip> --port <port>
   ```
   One Such example is:
   ```bash
   python __main__.py run --paig_deployment dev --config_path conf --host "127.0.0.1" --port 4545
   ```
   **Note:** *Admin user credentials.*
   ```bash
   PAIG URL: http://127.0.0.1:4545
   username: admin
   password: welcome1
   ```
   
## How to Start/Build Web UI <a name="webui"></a>
### Prerequisites
* **NodeJS:** =14.17.5

### Steps to run the development web UI
1. Fork the repository https://github.com/privacera/paig.
   ```bash
   git clone https://github.com/YOUR_USERNAME/paig.git
   ```
2. Change directory to the frontend/webapp repository
3. Install the dependencies
    ```bash
    npm install
    ```
4. Web UI configuration, including proxy configuration, can be found in the config/path.js file. Proxy should be set to web server url.
    ```js
    target: 'http://127.0.0.1:4545',
    ```
5. Run the web UI
    ```bash
    npm start
    ```
**Note:** *Admin user credentials.*
   ```bash
   username: admin
   password: welcome1
   ```

### How to Create Web UI Build with Script <a name="build"></a>
You can use the script to build the web UI. The script will create the build and copy the build to the backend templates folder.
1. Run the script to build the web UI.
   ```bash
   cd scripts
   source ./build_ui.sh
   ```
### How to Create Web UI Build Manually <a name="build"></a>
1. Change directory to the frontend/webapp repository<br/>
2. Run the command to install the dependencies
    ```bash
    npm install
    ```
3. Run the command to create the build
    ```bash
    npm run build
    ```
4. The build will be created in the public folder
5. Copy the build to the web server so that it can be served through the web server.
   ```bash
   mv public/styles/fonts  public/static/styles && rm -rf public/styles && cp -r public/*  ../../backend/paig/templates/
   ``` 
   

## Logging <a name="logging"></a>
PAIG provides a way to configure logging configurations and level.
You can edit [logging configuration](https://github.com/privacera/paig/blob/main/paig-server/backend/paig/conf/logging.ini) to customize logging for PAIG.