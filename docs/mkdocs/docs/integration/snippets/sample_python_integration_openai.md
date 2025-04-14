```python title="sample_python_integration.py" hl_lines="1 2 3 4 10 13 16 19 23 24 25 26 27 28 43 44 45 46 47 48 49 51 52 53"
from paig_client import client as paig_shield_client
from paig_client.model import ConversationType
import paig_client.exception
import uuid
from openai import OpenAI

# Set the OPENAI_API_KEY environment variable or set it here
openai_client = OpenAI()

# Initialize PAIG Shield 
# Set the PAIG_APP_API_KEY environment variable or set it here in the setup method
paig_shield_client.setup(frameworks=[])

# Replace "testuser" with the user who is using the application. Or you can use the service username
user = "testuser"

# Generate a random UUID which will be used to bind a prompt with a reply
paig_thread_id = str(uuid.uuid4())

try:
   with paig_shield_client.create_shield_context(username=user):
      prompt_text = "Who was the first President of USA and where did they live?"
      print(f"User Prompt: {prompt_text}")
      # Validate prompt with paig Shield
      updated_prompt_text = paig_shield_client.check_access(
         text=prompt_text,
         conversation_type=ConversationType.PROMPT,
         thread_id=paig_thread_id
      )
      updated_prompt_text = updated_prompt_text[0].response_text
      print(f"User Prompt (After PAIG Shield): {updated_prompt_text}")
      if prompt_text != updated_prompt_text:
         print(f"Updated prompt text: {updated_prompt_text}")

      # Call LLM with updated prompt text
      PROMPT = f"""Use the following pieces of context to answer the question at the end.     
        {updated_prompt_text}    
        ANSWER:
        """

      response = openai_client.chat.completions.create(model="gpt-4", messages=[{"role": "user", "content": PROMPT}],
                                                       temperature=0)
      llm_response = response.choices[0].message.content
      print(f"LLM Response: {llm_response}")
      # Validate LLM response with PAIG Shield
      updated_reply_text = paig_shield_client.check_access(
         text=llm_response,
         conversation_type=ConversationType.REPLY,
         thread_id=paig_thread_id
      )
      updated_reply_text = updated_reply_text[0].response_text
      print(f"LLM Response (After PAIG Shield): {updated_reply_text")
except paig_client.exception.AccessControlException as e:
   # If access is denied, then this exception will be thrown. You can handle it accordingly.
   print(f"AccessControlException: {e}")
```

1. !!! warning "OpenAI API Key"
   Don't forget to set `OPENAI_API_KEY` environment variable to your OpenAI API key.
