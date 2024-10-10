# PAIG SecureChat Web UI

Secure Chat provides a web interface to interact with the chat bot. It is a ReactJS based web application.

## Contents
- [How to Start Development Server](#developmentserver)

## How to Start Development Server <a name="developmentserver"></a>
### Prerequisites
* **NodeJS:** >=18.18.0

### Steps to run the development web UI
1. Clone the repository
2. Change directory to the web-ui repository
3. Install the dependencies
    ```bash
    npm install
    ```
4. Web UI configuration including proxy configuration can be found in package.json file. Proxy should be set to web server url.
    ```json
    "proxy": "http://localhost:3535"
    ```
5. Run the web UI
    ```bash
    npm start
    ```


