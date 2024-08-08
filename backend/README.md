# PAIG Opensource
PAIG is a web application that provides a platform for AI governance and audits that data. 

## Contents
- [Installation](#Installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Try Plugin code](#tryplugincode)


## Installation <a name="Installation"></a>
Privacera PAIG is a python library which can be installed using pip.
```bash
pip install paig_opensource
python -m spacy download en_core_web_lg
```

## Usage <a name="usage"></a>
Privacera PAIG  can be used in following ways:
1. **Run as a service:** You can simply run the PAIG as a service by running following command:
 ```bash
paig run
 ```
To get the help for the command and see all available [OPTIONS], you can run the following command:
```bash
paig --help
```
Example:
```bash
paig run --port 4545 --host 0.0.0.0
```
**Note:** *Admin user credentials.*
   ```bash
   username: admin
   password: welcome1
   ```
2. **Run as a library:** You can run PAIG in background by importing the library in your Python code. 
Please run the help command to see all available options you can pass while calling the launch_app method.
```python
from paig import launcher
# Start the PIAG
session = launcher.launch_app()
# To get active sessions
active_session = launcher.get_active_session()
print(active_session)
# To view the PIAG in the browser/Iframe
print(active_session.url)
# To view the PIAG in the Iframe
active_session.view()
# To stop the PIAG
launcher.close_app()
```

## Try Plugin code <a name="tryplugincode"></a>
1. Download the AI Application config from PAIG portal and save it in privacera folder.
  ```bash
  mkdir -p privacera
  ```
2. Setup your OpenAI key as an environment variable.
  ```bash
  export OPENAI_API_KEY=<API_KEY>
  ```
3. Initialize the Privacera Shield library:
<br>This one line of code will initialize the Privacera Shield library so that it is ready to protect your LangChain application.

    > **Tip:** If you get an error in this step, it could be because you have already run this step once. You can ignore the error and continue. You can also try restarting the Kernel and start from the beginning with the proper JSON file and OpenAI API key.

    ```python
    from privacera_shield import client as privacera_shield_client
    from openai import OpenAI
    
    # Set the OPENAI_API_KEY environment variable or set it here
    openai_client = OpenAI()
    
    privacera_shield_client.setup(frameworks=[])
    ```

4. Run the LLMChain with your question
   1. In this step, we are going to run the LLMChain with the prompt asked by a user named `testuser`.
   2. Note how we are passing the username by creating a Privacera Shield context object.
   3. Privacera Shield will intercept the prompt and the response coming from LLM for the `testuser` and run policies.
   4. The PAIG service scans both the prompt and response text and runs security policies.
   5. If the policies decide that the access is denied then an AccessControlException is thrown.

    > **Note:** Here username used is `testuser` which is an external user. So the policies applied will be as per the public. For applying userspecific properties, create and use the user from PAIG portal `Account > User Management > User`.
    
    ```python
    from privacera_shield import client as privacera_shield_client
    from privacera_shield.model import ConversationType
    import privacera_shield.exception
    import uuid
    
    # Replace "testuser" with the user who is using the application. Or you can use the service username
    user = "testuser"
    
    # Generate a random UUID which will be used to bind a prompt with a reply
    privacera_thread_id = str(uuid.uuid4())
    
    try:
       with privacera_shield_client.create_shield_context(username=user):
          prompt_text = "Who was the first President of USA and where did they live?"
          print(f"User Prompt: {prompt_text}")
          # Validate prompt with Privacera Shield
          updated_prompt_text = privacera_shield_client.check_access(
             text=prompt_text,
             conversation_type=ConversationType.PROMPT,
             thread_id=privacera_thread_id
          )
          updated_prompt_text = updated_prompt_text[0].response_text
          print(f"User Prompt (After Privacera Shield): {updated_prompt_text}")
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
          # Validate LLM response with Privacera Shield
          updated_reply_text = privacera_shield_client.check_access(
             text=llm_response,
             conversation_type=ConversationType.REPLY,
             thread_id=privacera_thread_id
          )
          updated_reply_text = updated_reply_text[0].response_text
          print(f"LLM Response (After Privacera Shield): {updated_reply_text}")
    except privacera_shield.exception.AccessControlException as e:
       # If access is denied, then this exception will be thrown. You can handle it accordingly.
       print(f"AccessControlException: {e}")
    ```

5. Review the access audits in PAIG portal under Security menu option
   1. Now you can log in to the PAIG portal and check under `Security > Access Audits` section. You will see the audit record for the above run of your LangChain application.
   2. You can click on the eye icon and see the details of the prompts sent by the application to the LLM and the responses coming from the LLM.
   3. The default policy in PAIG for the application monitors the flow and tags the contents of the prompt and response.


## Configuration <a name="configuration"></a>
Privacera PAIG Opensource provides overlay configuration. You can provide the custom configuration in the following ways:
1. Create a new directory in the present working directory of the project with the name custom-conf.
2. Create a new custom configuration file named dev_config.yaml in the custom-conf folder that is provided to the application.
3. In a custom configuration file, the user should provide new configuration key values or override the existing configuration. Example: custom-conf/dev_config.yaml
Example: `custom-conf/dev_config.yaml`
```yaml
account_services:
  database:
      url: "sqlite+aiosqlite:///db/database.db"

security:
  expire_minutes: 1440
  basic_auth:
    secret: "<secret>"
```
