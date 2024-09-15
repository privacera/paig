---
title: Quickstart
---

# Quickstart

This guide details the steps to install and start using the `paig_client`, a client library for integrating PAIG with your applications.

## Installation

To use `paig_client`, you first need to install it and its dependencies.

### Install or update Python

Ensure that you have Python 3.11 installed, as it is required for using `paig_client`. For instructions on installing Python, refer to the [official Python documentation](https://www.python.org/downloads/).

### Install PAIG Client

Install the latest release of `paig_client` via pip:

```bash
pip install paig_client
```

## Configuration

Before using `paig_client`, you need to set up your AI Application within the PAIG portal.

### Create AI Application

Navigate to **Application > AI Application** and click the **CREATE APPLICATION** button in the top right corner. Fill in the required details and click on **CREATE** to create your AI Application.

### Download Application Configuration File

Once you've created your AI Application, click the **DOWNLOAD APP CONFIG** button located in the top right corner of the application's page. Place the downloaded file in a folder called `privacera` relative to where you are running the application.


## Using PAIG Client

To use `paig_client` with Langchain, follow these steps:

You will need to install Langchain and other required dependencies for this example:

```bash
pip install langchain openai
```

**Export your OpenAI API key:**

   Make sure you export your OpenAI API key before running the program:

   ```bash
   export OPENAI_API_KEY=your-openai-api-key
   ```

**Run the following Python program:**

   This example demonstrates `paig_client` integration with Langchain:

   ```python
   import os
   import paig_client.client
   import paig_client.exception

   from langchain.llms import OpenAI
   from langchain.prompts import PromptTemplate
   from langchain.chains import LLMChain

   # Get the OpenAI API key from environment variables
   api_key = os.getenv("OPENAI_API_KEY")

   # Initialize PAIG client for Langchain integration
   paig_client.client.setup(frameworks=["langchain"])

   # Set up the Langchain LLM with OpenAI
   llm = OpenAI(openai_api_key=api_key)

   # Create a prompt template
   template = """Question: {question}

   Answer: Let's think step by step."""
   prompt = PromptTemplate(template=template, input_variables=["question"])

   # Define the user and the query
   user = "testuser"
   prompt_text = "Who is the first President of USA and where did they live?"

   # Create the LLMChain for executing the prompt
   llm_chain = LLMChain(prompt=prompt, llm=llm)

   try:
       # Create a PAIG context to enforce access controls
       with paig_client.client.create_shield_context(username=user):
           response = llm_chain.run(prompt_text)
           print(f"LLM Response: {response}")
   except paig_client.exception.AccessControlException as e:
       # Handle the case where access is denied
       print(f"AccessControlException: {e}")
   ```

**Monitor and Audit:**

   After running the program, you can monitor and audit the data access and retrieval operations by navigating to the **Security > Access Audits** section in the PAIG portal. This will allow you to review access logs and actions performed during the execution of your application.

**Modify Policies and Experiment:**

   Once you've successfully run your program, return to the PAIG portal and navigate to the application you created. Play around with policy settings, modify access control rules, and re-run your program to observe how changes affect data access.
