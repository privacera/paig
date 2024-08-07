## Contents
- [How to Start Development Server](#developmentserver)
- [Configuration](#configuration)
- [Logging](#logging)

## How to Start Development Server <a name="developmentserver"></a>
### Prerequisites
* **Python:** >=3.10

### Steps to run the development web Server
1. Clone the repository.
2. Change directory to the backend repository.
   ```bash
    cd backend
    ```
3. Create a virtual environment.
    ```bash
    python3 -m venv venv
    ```
4. Activate the virtual environment.
    ```bash
    source venv/bin/activate
    ```
5. Install the dependencies.
    ```bash
    pip install -r requirements.txt
    ```
6. Change directory to the paig.
    ```bash
    cd paig
    ```
7. Run the web server.
     ```bash
    python __main__.py run --paig_deployment dev|prod --config_path <path to config folder> --host <host_ip> --port <port>
        
     ```
     One Such example is:
     ```bash
     python __main__.py run --paig_deployment dev --config_path conf --host "localhost" --port 9090
        
     ```

### Steps to run the development web Server with web UI build
1. Follow steps 1 to 6 from above.
2. Change directory to the root level of the repository.
3. Run the script to build the web UI.
    ```bash
    cd scripts
    source ./build_ui.sh
    ```
4. Follow step 7 from above.