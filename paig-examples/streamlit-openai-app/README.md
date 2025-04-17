# Streamlit Examples
This repository provides a list of examples for users who want to use PAIG with their LLM applications. It includes multiple hands-on demos of PAIG's security and governance features for different scenarios.

## Contents
- [Installation](#installation)
- [Configuration](#configuration)

## Installation
To get started with the PAIG client and Streamlit demo:
<br>Go to streamlit-openai-app.
```shell
cd paig-examples/streamlit-openai-app
```
Run the install script, to install the required packages:
```shell
chmod +x install.sh
./install.sh
```

## Create a new AI application and Generate an API key
- To create a new application and generate an API key, follow these steps:
     - Login to PAIG.
     - Go to `Paig Navigator` → `AI Applications` and click the `CREATE APPLICATION` button at the top-right.
     - A dialog box will open where you can enter the details of your application.
     - Once the Application is created:
       - Navigate to `Paig Navigator` → `AI Applications` and select the application for which you want to generate the API key.
       - In the `API KEYS` tab, click the `GENERATE API KEY` button in the top-right corner.
       - Provide a `Name` and `Description`, and set an `Expiry`, or select the `Max Validity (1 year)` checkbox to use the default expiry.

       > **Note:** Once the API key is generated, it will not be shown again. Ensure you copy and securely store it immediately after generation.

   - To initialize the **PAIG Shield** library in your SecureChat application, export the `PAIG_APP_API_KEY` as an environment variable:

     ```bash
     export PAIG_APP_API_KEY=<<AI_APPLICATION_API_KEY>>
     ```
```shell
source venv/bin/activate
export PAIG_APP_API_KEY=<<AI_APPLICATION_API_KEY>>
streamlit run chatbot_simple.py
```
