# GET STARTED WITH PAIG SERVER

## REQUIREMENTS

- **Python** >=3.10
- **NodeJS** ==14.17.5 
- **OS** : Linux/Debian based

## CONTENTS
- [Setting Up the Backend](#setting-up-the-backend)
- [Setting up the Frontend](#setting-up-the-frontend)

# Before Set-Up
1. Fork the repository from https://github.com/privacera/paig

# Setting up the Backend
### Steps to run the development web Server
1. Clone the repository if not already cloned.
   ```bash
   git clone git@github.com:<username>/paig.git
   ```
2. Change directory to the paig-server.
   ```bash
   cd paig/paig-server
   ```
3. Run the script to build the web UI.
   ```bash
   cd scripts
   source ./build_ui.sh
   ```
4. Go to the backend directory.
   ```bash
   cd backend
   ```
5. Create a virtual environment.
    ```bash
    python -m venv venv
    ```
   OR
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
   python __main__.py run --paig_deployment dev|prod --config_path <path to config folder> --host <host_ip> --port <port> --background <true|false>
   ```
   **Note**: If any error comes true repeating **_step 3_** then try again

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

### PAIG Server Background Mode
PAIG can be run in the background mode by setting the background flag to true.

1. To Start the PAIG in the background mode:
```bash
python __main__.py run --background true
```
**Note:** Please use help command to see all available options you can pass on command line.
```bash
python __main__.py --help
```
2. To Stop the PAIG Server:
```bash
python __main__.py stop
```
3. To Check the status of the PAIG Server:
```bash
python __main__.py status
```

# Setting up the Frontend
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