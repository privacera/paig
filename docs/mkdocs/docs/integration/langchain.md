---
title: Integrating with LangChain
---

# LangChain

PAIG integration via LangChain is designed to be nearly touch-free. This is facilitated through the use of
PAIG Shield library, which transparently intercepts calls within LangChain, enforcing policies on the original prompt as
well as whenever prompts are altered, whether due to Chains or Retrieval Augmented Generation (RAG). The objective is to
ensure that policy adherence is seamlessly maintained across all interactions within the application, irrespective of
prompt modifications.

Here are the Quick Start options for trying out the integrations with LangChain.

1. **Google Colab Notebook:** You can experiment with the LangChain integration using a Google Colab notebook. This option only requires a Google account. Google Colab provides a free Jupyter notebook environment where you can run the PAIG SecureChat application.

2. **Sample Application:** You can download the sample application and run it in your local environment. This option requires Python to be installed locally.

For both options, you'll need to create a PAIG Shield Application in PAIG and download the corresponding configuration file.


## **Adding AI Application in PAIG**

As a first step, you need to add your AI Application in PAIG and we will use that application to integrate PAIG. 
If you already added the Application to the PAIG, then you can skip this step.

--8<-- "docs/integration/snippets/create_application.md"

## **Generate AI application API Key**

--8<-- "docs/integration/snippets/paig_apikey_generate.md"

## **Set the PAIG API Key**

To initialize the PAIG Shield library in your AI application, export the __PAIG_APP_API_KEY__ as an environment variable.

```shell
export PAIG_APP_API_KEY=<API_KEY>
```

!!! note "Alternative Method: Pass API Key in Code"
    If you prefer not to use environment variables, you can directly pass the API key when initializing the library:
    ```python
    paig_shield_client.setup(frameworks=["langchain"], application_config_api_key="<API_KEY>")
    ```
    For a complete code example showing where to place this, locate the `setup()` method in the provided [sample code](#sample-code) section below.

!!! info "Precedence Rule"
    If the __PAIG_APP_API_KEY__ is set both as an environment variable and in the code, the key specified in the code will take priority.


## **Using Google Colab Notebook**

After you have generated the API key, you can go to
<!-- md:go_to_google_collab https://colab.research.google.com/github/privacera/notebooks/blob/main/google-colab/paig_langchain_openai_colab.ipynb:Google Colab NoteBook -->

!!! note "Pre-requisite"
    1. You need to authorize the Google Colab to access GitHub


## **Using Python Sample Application**

The following are the prerequisites for trying out with LangChain

- [ ] LangChain needs python 3.11 and above

### **Sample Code**

If you like to try first and then understand the code later, then here is a sample application you can try it out 
quickly. The explanation of the code is provided [here](#ai_applications).

=== "OpenAI Example"

    !!! info "Supported versions"
        {{ read_csv('snippets/supported_versions_langchain_openai.csv') }}

    You can download 
    [sample_langchain_integration.py](snippets/sample_langchain_integration_openai.py){:download="sample_langchain_integration.py"} 
    and [requirements.txt](snippets/requirements_langchain_openai.txt){:download="requirements.txt"} for OpenAI

    ```python title="sample_langchain_integration.py" hl_lines="2 3 11 27 30"
    --8<-- "docs/integration/snippets/sample_langchain_integration_openai.py"
    ```
    ```txt title="requirements.txt" hl_lines="4"
    --8<-- "docs/integration/snippets/requirements_langchain_openai.txt"
    ```
    !!! info "Open AI Key"
    
        For OpenAI, you need to set the __OPENAI_API_KEY__ environment variable or set it in the code.
    <small>To export __OPENAI_API_KEY__ as an environment variable use the below command:</small>
    ```shell
    export OPENAI_API_KEY="<your-openai-api-key>"
    ```

=== "Bedrock Example"

    --8<-- "docs/integration/snippets/sample_langchain_integration_bedrock.md"

    !!! info "Dependent python package"
    
        Make sure you have installed the dependent python packages like boto3 and langchain

    !!! info "AWS IAM role access to Bedrock"

        Make sure you are running on AWS infrastructure which has access to Bedrock

---

It is recommended to use Python's virtual environment to run the sample application. The following steps show how to
create a virtual environment and run the sample application. Create a folder where where you want to run the sample. E.g.

```shell
mkdir -p ~/paig-sample
cd ~/paig-sample
```


**Create a virtual environment and activate it**
```shell
python3 -m venv venv
source venv/bin/activate
```

Install the required python packages
```shell
pip3 install -r requirements.txt
```

**Run the sample application**
```shell
python3 sample_langchain_integration.py
```

**Check the PAIG Lens Access Audits**
Now go to PAIG Lens Access Audits to check the prompts and responses for the `testuser`.

## **Code Breakup and explanation**

In your AI Application you need to initialize PAIG Shield library. Once it is initialized, it will automatically 
embed itself within the LangChain framework and intercept all requests made by user as well as the iterations
betweens agents and chains. The following code snippet shows how to initialize the PAIG Library.

### **Configure the [API Key](#set-the-paig-api-key)**

Export or Pass the generated API KEY from the portal as an environment variable: PAIG_APP_API_KEY=<API_KEY\> or Pass in the code(application_config_api_key=<API_KEY\>) in setup method.

### **Install paig_client**

PAIG Shield library needs to be first installed. This can be done by running the following command:

```shell
pip install paig_client
```

### **Importing the PAIG Libraries**
Add the following imports to your application

```python
import paig_client
from paig_client import client as paig_shield_client
```

### **Initializing the PAIG Library**

Call the setup method to initialize the PAIG Shield library.

```python
paig_shield_client.setup(frameworks=["langchain"])
```

### **Setting PAIG Shield Context**

Before calling Langchain, the PAIG Shield context needs to be set. This is primarily to set the user context

!!! note "Prompt User"
    --8<-- "docs/integration/snippets/snippet_user_in_context.md"

```python
try:
    with paig_shield_client.create_shield_context(username=user):
        response = llm_chain.invoke(prompt_text)
        print(f"LLM Response: {response.get('text')}")
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```

---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [User Guide](../../user-guide/)

-   :material-lightning-bolt-outline: __How To__

    [Manage Applications](../user-guide/manage-applications/index)
