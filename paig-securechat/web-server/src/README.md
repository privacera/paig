# PAIG Securechat 

Secure Chat is a conversational AI chatbot .
Secure chat allows users to create  conversations with an AI chatbot which can optionally be governed by PAIG. 
Secure chat library provides an easy to use, plugable platform which will allow developers/users to have open sourced chatbot python library.


## Contents
- [Installation](#Installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Configure PAIG Shield Config](#shieldconfigure)


## Installation <a name="Installation"></a>
PAIG Secure chat is a python library which can be installed using pip.
```bash
pip install paig_securechat
```

## Usage <a name="usage"></a>
PAIG Secure chat can be used in following ways:
1. Before starting the securechat, you need to create a PAIG application and generate an API key for the application.
   - To create a new application and generate an API key, follow these steps:
     
     - Login to PAIG.
     - Go to `Paig Navigator` → `AI Applications` and click the `CREATE APPLICATION` button at the top-right.
     - A dialog box will open where you can enter the details of your application.
     - Once the Application is created:
       
       - Navigate to `Paig Navigator` → `AI Applications` and select the application for which you want to generate the API key.
       - In the `API KEYS` tab, click the `GENERATE API KEY` button in the top-right corner.
       - Provide a `Name` and `Description`, and set an `Expiry`, or select the `Max Validity (1 year)` checkbox to use the default expiry.

       > **Note:** Once the API key is generated, it will not be shown again. Ensure you copy and securely store it immediately after generation.

   - To initialize the **PAIG Shield** library in your SecureChat application, export the `PAIG_APP_API_KEY` as an environment variable:

     ```bash
     export PAIG_APP_API_KEY=<<AI_APPLICATION_API_KEY>>
     ```

     **OR**  
     Create a file called `paig.key` in the `custom-configs` folder and save the AI Application API key in it:

     ```bash
     echo "<<AI_APPLICATION_API_KEY>>" > custom-configs/paig.key
     ```
2. **Run as a service:** You can simply run the secure chat as a service by running following command:
 ```bash
paig_securechat run
 ```
To get the help for the command and see all available [OPTIONS], you can run the following command:
```bash
paig_securechat --help
```
Example:
```bash
paig_securechat run --port 2324 --host 0.0.0.0 --openai_api_key <API_KEY> 
```
3. **Run as a library:** You can run PAIG Secure chat in background by importing the library in your python code.
Please run help command to see all available options you can pass while calling launch_app method.
```python
from paig_securechat import launcher
# Start the PAIG Secure Chatbot
session = launcher.launch_app()
# To start without PAIG Shield
# session = launcher.launch_app(disable_paig_shield_plugin=True)
# To get active sessions
active_session = launcher.get_active_session()
print(active_session)
# To view the chatbot in the browser/Iframe
print(active_session.url)
# To view the chatbot in the Iframe
active_session.view()
# To stop the chatbot
launcher.close_app()
```
> [!NOTE]
> We recommend to use PAIG Shield config for governance of the chatbot.You can opt for insecure mode by providing the `--disable_paig_shield_plugin` flag while running the chatbot. You can pass this option in launch_app method as well.

## Configuration <a name="configuration"></a>
PAIG Secure chat provides overlay configuration. You can provide the custom configuration in the following ways:
1. Create a new directory in the present working directory of the project with the name `custom-configs`.
2. Create a new custom configuration file named `standalone_config.yaml` in the `custom-configs` folder which is provided to the application.
3. In custom configuration file , user should provide new configuration key-values or override the existing configuration.
4. User can configure `response_if_no_docs_found` to provide a custom response when vector DB return no docs, If user want response from AI Model then set `response_if_no_docs_found` to `null`
<br>Example: `custom-configs/standalone_config.yaml`
```yaml
#MODELS CONFIG
AI_applications:
  file_path: "configs/AI_applications.json"
  default_implementation_class: "services.OpenAI_Application.OpenAIClient.OpenAIClient"
  response_if_no_docs_found: "I cannot answer this question as there was no context provided"
  sales_model:
    conversation_history_k: 5
    paig_shield_config_file: "custom-configs/privacera-shield-config.json"
    disable_conversation_chain: false
    vectordb:
      index_path: "securechat/sales/index"
      data_path: "securechat/sales/data"
      vector_type: "chroma"
```

## Configure PAIG Shield Config <a name="shieldconfigure"></a>
PAIG SecureChat provides an option to configure the PAIG Shield Config.
You can refer to standalone_config.yaml to see location of the shield config file.
All you need to do is to copy PAIG Shield Config file to the location mentioned in the standalone_config.yaml file.