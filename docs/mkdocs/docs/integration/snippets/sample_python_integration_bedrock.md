```python title="sample_python_integration.py" hl_lines="3 4 5 22 24 28 29 30 55 56 57 60 61 62"
import json

import paig_client
from paig_client import client as paig_shield_client
from paig_client.model import ConversationType
import boto3

# If needed, pdate the below 2 variables with your model name and region
model_name = "amazon.titan-tg1-large"
region = "us-west-2"

bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name=region,
)
accept = "application/json"
contentType = "application/json"

paig_shield_client.setup(frameworks=[])

# Replace "testuser" with the user who is using the application. Or you can use the service username
user = "testuser"
try:
    with paig_shield_client.create_shield_context(username=user):
        prompt_text = "Who was the first President of USA and where did they live?"
        print(f"User Prompt: {prompt_text}")
        # Validate prompt with Privacera Shield
        updated_prompt_text = paig_shield_client.check_access(
            text=prompt_text,
            conversation_type=ConversationType.PROMPT
        )
        print(f"User Prompt (After Privacera Shield): {prompt_text}")
        if prompt_text != updated_prompt_text:
            print(f"Updated prompt text: {updated_prompt_text}")

        # Call LLM with updated prompt text
        PROMPT = f"""Use the following pieces of context to answer the question at the end.     
        {updated_prompt_text}    
        ANSWER:
        """

        prompt_config = {
            "inputText": PROMPT
        }

        body = json.dumps(prompt_config)
        response = bedrock_runtime.invoke_model(modelId=model_name, body=body, accept=accept,
                                                contentType=contentType)

        response_body = json.loads(response.get("body").read())
        results = response_body.get("results")
        for result in results:
            reply_text = result.get('outputText')
            # Validate LLM response with Privacera Shield
            update_reply_text = paig_shield_client.check_access(
                text=reply_text,
                conversation_type=ConversationType.REPLY
            )
            print(f"LLM Response (After Privacera Shield): {update_reply_text}")
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```