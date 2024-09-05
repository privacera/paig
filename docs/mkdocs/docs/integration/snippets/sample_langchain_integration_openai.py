import os
import paig_client
from paig_client import client as paig_shield_client
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

api_key = os.getenv("OPENAI_API_KEY")  # (1)

# Initialize Privacera Shield
paig_shield_client.setup(frameworks=["langchain"])

llm = OpenAI(openai_api_key=api_key)
template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate(template=template, input_variables=["question"])

# Let's assume the user is "testuser"
user = "testuser"
prompt_text = "Who was the first President of USA and where did they live?"
print(f"Prompt: {prompt_text}")
print()

llm_chain = LLMChain(prompt=prompt, llm=llm)
try:
    with paig_shield_client.create_shield_context(username=user):
        response = llm_chain.invoke(prompt_text)
        print(f"LLM Response: {response.get('text')}")
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
