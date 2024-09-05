# PAIG Client Library

The `paig_client` library allows you to seamlessly integrate Privacera AI Governance into your Langchain projects. 

This README provides a step-by-step guide on how to set up and use the library.

## Installation

You can install the `paig_client` library using `pip`:

```shell
pip3 install paig_client
```

## Initialization
Start your PAIG-Server. Create your AI application and 
download the Shield Configuration file. Place the file in a folder called `privacera` relative to 
where you are running the app.

```python
# Import paig_client
import paig_client.client

# Setup Privacera Shield
paig_client.client.setup(frameworks=["langchain"])
```

## Usage
Once you have completed the setup of paig_client, you can set the user in the context 
for Privacera Shield to use.

### Using context manager

```python
import paig_client.client

paig_client.client.setup(frameworks=["langchain"])

# Set the current user_name in the context
try:
    with paig_client.client.create_shield_context(username="user"):
        response = llm_chain.run(prompt_text)
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```

# Completed example using OpenAI

```python
import os

import paig_client.client
import paig_client.exception

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

api_key=os.getenv("OPENAI_API_KEY") # 

# Initialize Privacera Shield
paig_client.client.setup(frameworks=["langchain"])

llm = OpenAI(openai_api_key=api_key)
template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate(template=template, input_variables=["question"])

# Let's assume the user is "testuser"
user = "testuser"
prompt_text = "Who is first President of USA and where did they live?"
llm_chain = LLMChain(prompt=prompt, llm=llm)
try:
   with paig_client.client.create_shield_context(username=user):
      response = llm_chain.run(prompt_text)
      print(f"LLM Response: {response}")
except paig_client.exception.AccessControlException as e:
   # If access is denied, then this exception will be thrown. You can handle it accordingly.
   print(f"AccessControlException: {e}")

```

### Additional ways of passing the application config file to set up Privacera Shield
- Place the file in ```privacera``` folder relative to where you are running the app
- Set the environment variable ```PRIVACERA_SHEILD_CONFIG_FILE``` to the path of the file
- Set the environment variable ```PRIVACERA_SHEILD_CONFIG_DIR``` to a folder that contains the file. Only one
  application config file should be present in the folder.
- Pass the file path as ```application_config_file``` parameter to the setup function
- Pass the string contents of the file to the setup function as ```application_config``` parameter
- Pass a dict by converting file contents which is in json format and pass to the setup function as 
  ```application_config``` parameter

### You can create multiple applications

If your application has multiple AI models to be governed, you can create multiple applications as follows:

```python
app1 = paig_client.client.setup_app(...)
app2 = paig_client.client.setup_app(...)
```
You can pass the following parameters to the setup_app function:
- Pass the file path as ```application_config_file``` parameter to the setup function
- Pass the string contents of the file to the setup function as ```application_config``` parameter
- Pass a dict by converting file contents which is in json format and pass to the setup function as 
  ```application_config``` parameter

And then you can pass the application object to the context manager as follows:

```python
with paig_client.client.create_shield_context(appplication=app1, username="user"):
    response = llm_chain.run(prompt_text)
```

Note that you still need to invoke the privacera.client.setup() method before calling the 
privacera.client.setup_app(...) method.
