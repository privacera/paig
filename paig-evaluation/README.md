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
To get the help for the command and see all available [OPTIONS], you can run the following command:
```bash
paig_evaluation --help
```

Example:
```bash
paig_evaluation run --paig_eval_config paig_eval_config.json --openai_api_key <API_KEY> 
```

Note: You can also set the OPENAI_API_KEY as an environment variable.

Sample paig_eval_config.json file: [sample_paig_eval_config.json](sample_paig_eval_config.json)

