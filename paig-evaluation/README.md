## PAIG Evaluation

PAIG Evaluation is a python library which used to scan and evaluate the GenAI Application.

## Prerequisites
* **Python:** >=3.11
* **Node:** >=18.20.5



## Installation <a name="Installation"></a>
Install npm dependencies
```bash
npm install promptfoo@0.102.4
```


PAIG Evaluation is a python library which can be installed using pip.
```bash
pip install paig_evaluation
```


## Usage <a name="usage"></a>
PAIG Evaluation can be used in following ways:
1. **Run as a service:** You can simply run the evaluation as a service by running following command:
    ```bash
    paig_evaluation run --paig_eval_config <json file path> --openai_api_key <your OPENAI API Key>
    ```
2. To get the help for the command and see all available [OPTIONS], you can run the following command:
    ```bash
    paig_evaluation --help
    ```
    Example:
    ```bash
    paig_evaluation run --paig_eval_config paig_eval_config.json --openai_api_key <API_KEY> 
    ```

    __Note__: You can also set the OPENAI_API_KEY as an environment variable.

    Sample paig_eval_config.json file: [paig_eval_config.json](paig_evaluation/paig_eval_config.json)
3. Generate setup config:
    ```bash
    paig_evaluation setup --application_config <json file path>
    ```
    This command will generate a sample setup config on console. Sample application_config.json file: [application_config.json](paig_evaluation/application_config.json)
    <br>__Note__: This generated setup config you can copy to paig_eval_config.json file and run the evaluation again.

