---
title: Integrating with Python Applications
---

# Python Applications

If your AI application is developed in Python and not using LangChain, you can integrate PAIG with your application
using the PAIG Python library. With this option you also have an option to customize the flow and decide when to invoke
PAIG.

## **Install paig_client**

PAIG client library needs to be first installed. This can be done by running the following command:

```shell
pip install paig_client
```

## **Adding AI Application in PAIG**

As a first step, you need to add your AI Application in PAIG and we will use that application to integrate PAIG.
If you already added the Application to the PAIG, then you can skip this step.

--8<-- "docs/integration/snippets/create_application.md"

## **Generate AI application API key**

--8<-- "docs/integration/snippets/paig_apikey_generate.md"

## **Set the PAIG API Key**

To initialize the PAIG Shield library in your AI application, export the __PAIG_APP_API_KEY__ as an environment variable.

```shell
export PAIG_APP_API_KEY=<API_KEY>
```

!!! note "Alternative Method: Pass API Key in Code"
    If you prefer not to use environment variables, you can directly pass the API key when initializing the library:
        ```python
        paig_shield_client.setup(frameworks=[], application_config_api_key="<API_KEY>")
        ```
    For a complete code example showing where to place this, locate the `setup()` method in the provided [sample code](#sample-code) section below.

!!! info "Precedence Rule"
    If the __PAIG_APP_API_KEY__ is set both as an environment variable and in the code, the key specified in the code will take priority.


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

**Run the sample application**
```shell
python sample_python_integration.py
```

``` title="Output" linenums="0" hl_lines="2 4"
User Prompt: Who was first President of USA and where did they live?
LLM Response: The first President of the USA was George Washington. He lived in Mount Vernon, Virginia.
User Prompt (After PAIG Shield): Who is first President of USA and where did they live?
LLM Response (After PAIG Shield): The first President of the USA was <<PERSON>>. He lived in Mount Vernon, Virginia.
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

Call the setup method to initialize the PAIG Shield library. Since you are not using any frameworks, you can pass
an empty list to the setup method.

```python
paig_shield_client.setup(frameworks=[])
```

Generate a random UUID which will be used to bind a prompt with a response
```python
paig_thread_id = str(uuid.uuid4())
```
**Checking Access Before Sending Prompt to LLM**
!!! note "Prompt User"
    --8<-- "docs/integration/snippets/snippet_user_in_context.md"

```python
try:
    with paig_shield_client.create_shield_context(username=user):
        # Validate prompt with PAIG Shield
        updated_prompt_text = paig_shield_client.check_access(
            text=prompt_text,
            conversation_type=ConversationType.PROMPT,
            thread_id=paig_thread_id
        )
        updated_prompt_text = updated_prompt_text[0].response_text
        print(f"User Prompt (After PAIG Shield): {updated_prompt_text}")
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```

**Checking Access After Receiving Response from LLM**
```python
try:
    with paig_shield_client.create_shield_context(username=user):
        # Validate LLM response with PAIG Shield
        updated_reply_text = paig_shield_client.check_access(
            text=llm_response,
            conversation_type=ConversationType.REPLY,
            thread_id=paig_thread_id
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

---
:octicons-tasklist-16: **What Next?**

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: __Read More__

    [User Guide](../../user-guide/)

-   :material-lightning-bolt-outline: __How To__

    [Manage Applications](../user-guide/manage-applications/index.md)
