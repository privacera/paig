# PAIG Client Library

The `paig_client` library allows you to seamlessly integrate Privacera AI Governance into your Langchain projects. 

This README provides a step-by-step guide on how to set up and use the library.

## Installation

You can install the `paig_client` library using `pip`:

```shell
pip3 install paig_client
```

## Initialization
Start your PAIG-Server. Create your AI application and generate API key.
Set the `PAIG_APP_API_KEY` as environment variable.

```python
# Import paig_client
import paig_client.client

# Setup PAIG Shield
# Set the PAIG_APP_API_KEY environment variable or set it here in the setup method
paig_client.client.setup(frameworks=["langchain"])
```

## Usage
Once you have completed the setup of paig_client, you can set the user in the context 
for PAIG Shield to use.

### Using context manager

```python
import paig_client.client

# Set the PAIG_APP_API_KEY environment variable or set it here in the setup method
paig_client.client.setup(frameworks=["langchain"])

# Set the current user_name in the context
try:
    with paig_client.client.create_shield_context(username="user"):
        response = llm_chain.run(prompt_text)
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```

### Code Example
You can refer to the [Sample Code](../../integration/python-applications.md).


### Additional ways of passing the PAIG_APP_API_KEY to set up Privacera Shield

!!! note "Alternative Method: Pass API Key in Code"
    If you prefer not to use environment variables, you can directly pass the API key when initializing the library:
        ```python
        paig_shield_client.setup(frameworks=[], application_config_api_key="<API_KEY>")
        ```
    For a complete code example showing where to place this, locate the `setup()` method in the provided [sample code](#sample-code) section below.

!!! info "Precedence Rule"
    If the __PAIG_APP_API_KEY__ is set both as an environment variable and in the code, the key specified in the code will take priority.


### You can create multiple applications

If your application has multiple AI models to be governed, you can create multiple applications as follows:

```python
app1 = paig_client.client.setup_app(application_config_api_key="<API_KEY>")
app2 = paig_client.client.setup_app(application_config_api_key="<API_KEY>")
```

- Pass the api key as ```application_config_api_key="<API_KEY>"``` parameter to the setup function

And then you can pass the application object to the context manager as follows:

```python
with paig_client.client.create_shield_context(appplication=app1, username="user"):
    response = llm_chain.run(prompt_text)
```

Note that you still need to invoke the privacera.client.setup() method before calling the 
privacera.client.setup_app(...) method.
