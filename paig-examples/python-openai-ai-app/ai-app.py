from paig_client import client as paig_shield_client
from paig_client.model import ConversationType
import paig_client.exception
from openai import OpenAI
import uuid

# Set the OPENAI_API_KEY environment variable or set it here
openai_client = OpenAI()

paig_shield_client.setup(frameworks=[])

# Model
MODEL = "gpt-4o"

# Replace "testuser" with the user who is using the application. Or you can use the service username
user = "testuser"

try:
    # Generate a random UUID which will be used to bind a prompt with a reply
    random_uuid_str = str(uuid.uuid4())
    with paig_shield_client.create_shield_context(username=user):
        prompt_text = "Who was the first President of USA and where did they live? Write 300 words on it"
        print(f"User Prompt: {prompt_text}")
        # Validate prompt with PAIG Shield
        updated_prompt_text = paig_shield_client.check_access(
            text=prompt_text,
            conversation_type=ConversationType.PROMPT,
            thread_id=random_uuid_str
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
        response = openai_client.chat.completions.create(model=MODEL, messages=[{"role": "user", "content": PROMPT}],
                                                         temperature=0)
        llm_response = response.choices[0].message.content
        print(f"LLM Response: {llm_response}")
        # Validate LLM response with PAIG Shield
        updated_reply_text = paig_shield_client.check_access(
            text=llm_response,
            conversation_type=ConversationType.REPLY,
            thread_id=random_uuid_str
        )
        print(f"LLM Response (After PAIG Shield): {updated_reply_text[0].response_text}")
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
