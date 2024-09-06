---
title: Integrating with Python Applications
---

# Python Applications

If your AI application is developed in Python and not using LangChain, you can integrate PAIG with your application
using the PAIG Python library. With this option you also have an option to customize the flow and decide when to invoke
PAIG.

## **Install paig_client**

Privacera's plugin library needs to be first installed. This can be done by running the following command:

```shell
pip install paig_client
```

## **Adding AI Application in PAIG**

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

As a first step, you need to add your AI Application in PAIG and we will use that application to integrate PAIG.
If you already added the Application to the PAIG, then you can skip this step.

--8<-- "docs/integration/snippets/create_application.md"

## **Downloading Privacera Shield Configuration File**

<!-- md:go_to_paig /#/ai_applications:Go To PAIG -->

--8<-- "docs/integration/snippets/download_application_config.md"

## **Sample Code**

Here is a sample application you can try it out.

**Create a sample Python file**
Create a file called something like sample_python_integration.py and copy the following code snippet into it.

```shell
vi sample_python_integration.py
```

=== "OpenAI Example"

    --8<-- "docs/integration/snippets/sample_python_integration_openai.md"

    !!! info "Open AI Key"
    
        For OpenAI, you need to set the __OPENAI_API_KEY__ environment variable or set it in the code.

    !!! info "OpenAI python package"
    
        Make sure have installed the OpenAI python package.

=== "Bedrock Example"

    --8<-- "docs/integration/snippets/sample_python_integration_bedrock.md"

    !!! info "boto3 python package"
    
        Make sure you have installed the boto3 python package.

    !!! info "AWS IAM role access to Bedrock"

        Make sure you are running on AWS infrastructure which has access to Bedrock


**Copy Privacera Shield configugration file to the privacera folder**

```shell
mkdir -p privacera
#Copy the Privacera Shield Application configuration file to the privacera folder
```

**Run the sample application**
```shell
python sample_python_integration.py
```

``` title="Output" linenums="0" hl_lines="2 4"
User Prompt: Who was first President of USA and where did they live?
LLM Response: The first President of the USA was George Washington. He lived in Mount Vernon, Virginia.
User Prompt (After Privacera Shield): Who is first President of USA and where did they live?
LLM Response (After Privacera Shield): The first President of the USA was <<PERSON>>. He lived in Mount Vernon, Virginia.
```

## **Code Breakup and explanation**

In your AI Application you need to initialize and call the PAIG Library APIs before the prompts are sent to the LLM and
after the response is received from the LLM. If you are using multi-chain then you need to call the PAIG Library APIs
before and after each chain invocation. The following code snippet shows how to initialize the PAIG Library and
call the APIs:

**Importing the PAIG Libraries**
```python
from paig_client import client as paig_shield_client
from paig_client.model import ConversationType
import paig_client.exception
import uuid
```

**Initializing the PAIG Library**

Call the setup method to initialize the Privacera Shield library. Since you are not using any frameworks, you can pass
an empty list to the setup method.

```python
paig_shield_client.setup(frameworks=[])
```

Generate a random UUID which will be used to bind a prompt with a response
```python
privacera_thread_id = str(uuid.uuid4())
```
**Checking Access Before Sending Prompt to LLM**
!!! note "Prompt User"
    --8<-- "docs/integration/snippets/snippet_user_in_context.md"

```python
try:
    with paig_shield_client.create_shield_context(username=user):
        # Validate prompt with Privacera Shield
        updated_prompt_text = paig_shield_client.check_access(
            text=prompt_text,
            conversation_type=ConversationType.PROMPT,
            thread_id=privacera_thread_id
        )
        updated_prompt_text = updated_prompt_text[0].response_text
        print(f"User Prompt (After Privacera Shield): {updated_prompt_text}")
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```

**Checking Access After Receiving Response from LLM**
```python
try:
    with paig_shield_client.create_shield_context(username=user):
        # Validate LLM response with Privacera Shield
        updated_reply_text = paig_shield_client.check_access(
            text=llm_response,
            conversation_type=ConversationType.REPLY,
            thread_id=privacera_thread_id
        )
        updated_reply_text = updated_reply_text[0].response_text
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```

The conversation type is used to differentiate between the prompt, RAG and the reply. Here are the valid values:

- **Prompt** - `ConversationType.PROMPT`
- **RAG** - `ConversationType.RAG`
- **Reply** - `ConversationType.REPLY`

**Privacera Shield Application configuration file**

Create a folder called `privacera` in your application and copy the Privacera Shield Application configuration file


---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [User Guide](../../user-guide/)

-   :material-lightning-bolt-outline: __How To__

    [Manage Applications](../user-guide/manage-applications/index)
