# PAIG Evaluation

**PAIG Evaluation** is a Python library designed to scan and evaluate GenAI applications effectively.

---

## Prerequisites

Before using PAIG Evaluation, ensure the following dependencies are installed:

- **Python**: >= 3.11  
- **Node.js**: >= 18.20.5  

---

## Installation

### 1. Install npm Dependencies

Use npm to install the required dependencies:  
```bash
npm install promptfoo@0.102.4
```

### 2. Install the PAIG Evaluation Library

You can install the PAIG Evaluation Python library using pip:  
```bash
pip install paig_evaluation
```


__TODO__ : After publishing the package on pypi, we need to update below usage commands.
### 3. Build locally and use as library
To build the package locally and use it as a library, follow the steps below:
1. Clone the repository:
   ```bash
   git clone git@github.com:privacera/paig.git
   ```

2. Change the directory to the `paig-evaluation` folder:
   ```bash
   cd paig/paig-evaluation
   ```

3. Create a virtual environment:
   ```bash
    python -m venv venv
    ```

4. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```
5. Install build package
    ```bash
    pip install build
    ```

6. Build paig_evaluation package locally:
    ```bash
   python -m build -w
    ```

7. Install build package:
    ```bash
    pip install dist/*
    ```

8. Import and use as library:
    ```python
    from paig_evaluation.paig_eval import PaigEval


   # you can pass output_directory as variable where config and report files will be saved
   # you can pass openai_api_key as variable to set OpenAI API Key or you can set it as environment variable
   # if not provided, it will be saved under 'workdir' directory in current directory
   # Example: PaigEval(output_directory="<output_dir>", openai_api_key="<your_openai_api_key>")
   eval_obj = PaigEval(output_directory="new_workdir")
   
   
   application_config = {
       "application_name": "IT Support Chatbot",
       "purpose": "To support IT helpdesk",
       "application_client": "openai:gpt-4o-mini" # If not provided Default application cline is openai:gpt-4o-mini"
   }
   
   # Input for init_setup method is the application configuration JSON file like above
   config_plugins = eval_obj.init_setup(application_config=application_config)
   print("Config plugins::::", config_plugins)
   
   # Output of the above code snippet will be:
   """
   Config plugins:::: {
       "application_name": "IT Support Chatbot",
       "purpose": "To support IT helpdesk",
       "application_client": "openai:gpt-4o-mini",
       "categories": [
           "pii",
           "excessive-agency",
           "hallucination",
           "hijacking",
           "harmful:cybercrime",
           "pii:api-db",
           "pii:direct",
           "pii:session",
           "pii:social",
           "harmful:privacy"
       ]
   }
   """

   
   # Input for generate_prompts method is the config_with_plugins JSON file like above
   # This will generate config yaml file with prompts and save it under output directory
   # You can append "numTests": 2, in above config_plugins, If not provided then Default number of tests is 5
   eval_obj.generate_prompts(config_with_plugins=config_plugins)
   
   
   user_prompts_list = [
       {
           "vars": {
               "prompt": "Can you tell me jokes about bananas?"
           },
           "assert": [
               {
                   "type": "llm-rubric",
                   "value": "ensure that the output is funny"
               }
           ]
       },
       {
           "vars": {
               "prompt": "Can you tell me benefits of bananas?"
           },
           "assert": [
               {
                   "type": "llm-rubric",
                   "value": "ensure that the output is informative"
               }
           ]
       }
   ]
   
   # Input for append_user_prompts method is the user_prompts_list like above
   # Will append above tests in the config yaml file
   eval_obj.append_user_prompts(user_prompts_list=user_prompts_list)
   
   
   # Run the evaluation using the generated config yaml file
   # This will run the evaluation and return the report in JSON format, and save it under output directory
   report = eval_obj.run()
   print("Evaluation report::::", report)
   ```






## Usage
### 1. Setup Development Environment
To setup the development environment, follow the steps below:
1. Clone the repository:
   ```bash
   git clone git@github.com:privacera/paig.git
   ```

2. Change the directory to the `paig-evaluation` folder:
   ```bash
   cd paig/paig-evaluation
   ```

3. Create a virtual environment:
   ```bash
    python -m venv venv
    ```
   OR
   ```bash
    python3 -m venv venv
    ```
4. Activate the virtual environment
    ```bash
    source venv/bin/activate
    ```

5. Change the directory to the `paig_evaluation` and Install the dependencies:
    ```bash
    cd paig_evaluation
   ```
   Install the dependencies
    ```bash
    pip install -r requirements.txt
    ```


### 2. Generate Configs and Run Evaluation

PAIG Evaluation provides multiple commands for generating configurations and running evaluations. Below are the steps to use the library effectively:

#### 1. Generate Intermediate Application Config with Suggested Plugins
This command generates an intermediate application configuration with suggested plugins and saves it as `application_config_with_plugins.json` in the `workdir` directory.

```bash
python __main__.py init_setup
```
Default configuration file is `application_config.json`. You can pass the configuration file path as an argument to the command.
```bash
python __main__.py init_setup --application_config <your_config_json_file_path> --openai_api_key <your_openai_api_key>
```
__Note__: You can set OPENAI_API_KEY as an environment variable to avoid passing it as an argument.
```bash
export OPENAI_API_KEY=<your_openai_api_key>
```
- You can refer to a sample configuration file here: [application_config.json](paig_evaluation/application_config.json).
---

#### 2. Generate Setup Config

To generate a setup configuration, use:
This command uses intermediate application configuration and generate a setup configuration. 
The generated setup config is saved into `application_setup_config.json` in the `workdir` directory.
```bash
python __main__.py setup
```
---
#### 3. Generate Evaluation Config with prompts
This command uses setup configuration and generate evaluation configuration with prompts.
The generated evaluation config is saved into `paig_eval_config_with_prompts.yaml` in the `workdir` directory.
```bash
python __main__.py generate
```

#### 4. Run the Evaluation

Run the evaluation using the following command: 
This command uses evaluation configuration and runs the evaluation.
```bash
python __main__.py run
```

- This command executes the evaluation and outputs report write into `paig_eval_output_report.json` under `workdir` directory.  
