```python title="sample_langchain_integration.py" hl_lines="3 4 10 26 29"
import os

import paig_client
from paig_client import client as paig_shield_client
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Inititialize Privacera Shield
paig_shield_client.setup(frameworks=["langchain"])

model_name = "amazon.titan-tg1-large"
region = "us-west-2"
llm = Bedrock(model_id=model_name, region_name=region)

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate(template=template, input_variables=["question"])

# Let's assume the user is "testuser"
user = "testuser"
prompt_text = "Who was the first President of USA and where did they live?"
llm_chain = LLMChain(prompt=prompt, llm=llm)
try:
    with paig_shield_client.create_shield_context(username=user):
        response = llm_chain.run(prompt_text)
        print(f"LLM Response: {response}")
except paig_client.exception.AccessControlException as e:
    # If access is denied, then this exception will be thrown. You can handle it accordingly.
    print(f"AccessControlException: {e}")
```
