# GET STARTED WITH PAIG SERVER

## REQUIREMENTS

- **Python** >=3.10
- **NodeJS** ==14.17.5 
- **OS** : Linux/Debian based

# Fork and Clone the repository
1. Fork the repository from https://github.com/privacera/paig
2. Clone the repository if not already cloned.
   ```bash
   git clone git@github.com:<username>/paig.git
   ```

# Backend Set-Up

### Steps to run the development web Server
1. Run the script to build the web UI.
   ```bash
   cd paig/paig-server/scripts
   source ./build_ui.sh
   ```
2. Create a virtual environment in the backend directory.
    ```bash
    cd ../backend
    python -m venv venv
    ```
   OR
   ```bash
    cd ../backend
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
9. Run the web server.
   ```bash
   cd paig
   python __main__.py run --paig_deployment dev|prod --config_path <path to config folder> --host <host_ip> --port <port> --background <true|false>
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

### PAIG Server Commands

| Command | Description |
|---------|------------|
| python __main__.py run | Start PAIG Server using default options |
| python __main__.py run --background true | Start PAIG Server in background mode |
| python __main__.py --help | View all available command-line options |
| python __main__.py stop | Stop the PAIG Server |
| python __main__.py status | Check the status of the PAIG Server |

# Frontend Set-Up

### Steps to run the development web UI
1. Change directory to the frontend/webapp repository
2. Install the dependencies
    ```bash
    npm install
    ```
3. Web UI configuration, including proxy configuration, can be found in the config/path.js file. Proxy should be set to web server url.
    ```js
    target: 'http://127.0.0.1:4545',
    ```
4. Run the web UI
    ```bash
    npm start
    ```
**Note:** *Admin user credentials.*
   ```bash
   username: admin
   password: welcome1
   ```
