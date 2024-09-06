---
title: Integrating with LangChain
---

# LangChain

Privacera’s integration via LangChain is designed to be nearly touch-free. This is facilitated through the use of
Privacera's Shield library, which transparently intercepts calls within LangChain, enforcing policies on the original prompt as
well as whenever prompts are altered, whether due to Chains or Retrieval Augmented Generation (RAG). The objective is to
ensure that policy adherence is seamlessly maintained across all interactions within the application, irrespective of
prompt modifications.

Here are the Quick Start options for trying out the integrations with LangChain.

1. **Google Colab Notebook:** You can experiment with the LangChain integration using a Google Colab notebook. This option only requires a Google account. Google Colab provides a free Jupyter notebook environment where you can run the Privacera SecureChat application.

2. **Sample Application:** You can download the sample application and run it in your local environment. This option requires Python to be installed locally.

For both options, you'll need to create a Privacera Shield Application in PAIG and download the corresponding configuration file.


## **Adding AI Application in PAIG**

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

As a first step, you need to add your AI Application in PAIG and we will use that application to integrate PAIG. 
If you already added the Application to the PAIG, then you can skip this step.

--8<-- "docs/integration/snippets/create_application.md"

## **Downloading Privacera Shield Configuration File**

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

--8<-- "docs/integration/snippets/download_application_config.md"


## **Using Google Colab Notebook**

After you have downloaded the Privacera Shield configuration file, you can go to
<!-- md:go_to_google_collab https://colab.research.google.com/github/privacera/notebooks/blob/main/paig_langchain_openai.ipynb:Google Colab NoteBook -->

!!! note "Pre-requisite"
    1. You need to authorize the Google Colab to access GitHub


## **Using Python Sample Application****

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

    1. !!! warning "OpenAI API Key"
       Don't forget to set `OPENAI_API_KEY` environment variable to your OpenAI API key.

    !!! info "Open AI Key"
    
        For OpenAI, you need to set the __OPENAI_API_KEY__ environment variable or set it in the code.

    ```txt title="requirements.txt" hl_lines="4"
    --8<-- "docs/integration/snippets/requirements_langchain_openai.txt"
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

**Copy Privacera Shield configuration file to the privacera folder**
```shell
mkdir -p privacera
```
Copy the Privacera Shield Application configuration file to the `privacera` folder. It is okay not rename the config 
file name. E.g.

```shell
cp ~/Downloads/privacera-shield-SecureChat-config.json privacera/
```

If you are using OpenAI, then you need to set the OPENAI_API_KEY environment variable or set it in the code.

```shell
export OPENAI_API_KEY="<your-openai-api-key>"
```

**Run the sample application**
```shell
python3 sample_langchain_integration.py
```

**Check the security audits**
Now go to [Security Audits](/#/audits_security){:target="_blank"} to check the prompts and response for the `testuser`.

## **Code Breakup and explanation**

In your AI Application you need to initialize Privacera Shield library. Once it is initialized, it will automatically 
embed itself within the LangChain framework and intercept all requests made by user as well as the iterations
betweens agents and chains. The following code snippet shows how to initialize the PAIG Library.

### **Copy the Privacera Shield Application configuration file**

Create a folder called `privacera` in your application and copy the Privacera Shield Application configuration file

### **Install paig_client**

Privacera's Shield library needs to be first installed. This can be done by running the following command:

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

Call the setup method to initialize the Privacera Shield library.

```python
paig_shield_client.setup(frameworks=["langchain"])
```

### **Setting Privacera Shield Context**

Before calling Langchain, the Privacera Shield context needs to be set. This is primarily to set the user context

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
