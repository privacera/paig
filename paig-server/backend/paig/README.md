## Contents
- [Technology Stack](#technology-stack)
- [How to Start Development Server](#developmentserver)
- [Optional Configuration](#configuration)
- [How to Start/Build Web UI](../../paig-server/frontend/README.md)
- [PAIG Server Background Mode](#backgroundmode)
- [How to Setup Database](#databsesetup)
- [Logging](#logging)

## Technology Stack <a name="technology-stack"></a>
PAIG provides a platform for AI governance. It allows users to governance and audits the data on one platform. 
<br>PAIG uses the following technologies:
* **Web Application Framework:** ReactJS
* **Backend:** FastAPI (Python)
* **Database:** Relational Database (default sqlite)

## How to Start Development Server <a name="developmentserver"></a>
### Prerequisites
* **Python:** >=3.10
* **NodeJS:** =14.17.5

### Steps to run the development web Server
1. Clone the repository.
   ```bash
   git clone git@github.com:privacera/paig.git
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
   One Such example is:
   ```bash
   python __main__.py run --paig_deployment dev --config_path conf --host "127.0.0.1" --port 4545 --background true
   ```
   **Note:** *Admin user credentials.*
   ```bash
   PAIG URL: http://127.0.0.1:4545
   username: admin
   password: welcome1
   ```

## PAIG Server Background Mode <a name="backgroundmode"></a>
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


## Optional Configuration <a name="configuration"></a>
PAIG provides overlay configuration. PAIG will use the default configuration provided in the [default_config.yaml](conf/default_config.yaml) file.
This default configuration can be overridden by the user-provided custom configuration.
The user can provide the custom configuration in the following ways:
1. Create a new custom configuration file in the custom folder that is provided to the application.
2. The naming convention for the custom configuration file should be as follows:
   ```bash
   <ENVIRONMENT_NAME>_config.yaml
   ```
   For example:
   ```bash
   dev_config.yaml
   ```
   _Note-_ ENVIRONMENT_NAME is also referred to as PAIG_DEPLOYMENT in the application.
3. In a custom configuration file, the user should provide new configuration key values or override the existing configuration.
<br>Example: [custom-conf/dev_config.yaml](conf/default_config.yaml)

## How to Setup Database <a name="databsesetup"></a>
PAIG supports automatic as well as manual database creation/updation. Please refer to Database for more details.
[How to setup database](alembic_db/README.md)

## Logging <a name="logging"></a>
PAIG provides a way to configure logging configurations and level.
You can edit [logging configuration](conf/logging.ini) to customize logging for PAIG.