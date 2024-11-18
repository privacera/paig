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

## Configuration

Download the [Paig Shield Configuration](https://docs.paig.ai/integration/python-applications.html#downloading-privacera-shield-configuration-file) file, and place it in the `privacera` directory.

Once all the required packages are installed and configurations are set up, start the streamlit server within the virtual environment.

```shell
source venv/bin/activate
streamlit run chatbot_simple.py
```
