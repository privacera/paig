# PAIG Web UI

PAIG is a web application that provides a platform for AI governance and audits that data.

## Contents
- [How to Start Development Server](#developmentserver)
- [How to Create Build](#build)

## How to Start Development Server <a name="developmentserver"></a>
### Prerequisites
* **NodeJS:** =14.17.5

### Steps to run the development web UI
1. Clone the repository with submodules
    ```bash
    git clone git@github.com:privacera/paig.git
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
### How to Create Build <a name="build"></a>
You can simply create the build by running the following commands:
```bash
cd scripts
source ./build_ui.sh
```
You can run following commands to create the build manually:
1. Change directory to the frontend/webapp repository
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


