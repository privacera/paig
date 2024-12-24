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

---

## Usage

PAIG Evaluation provides multiple commands for generating configurations and running evaluations. Below are the steps to use the library effectively:

#### 1. Generate Intermediate Application Config with Suggested Plugins

Run the following command to create an intermediate application configuration file with suggested plugins:  
```bash
python __main__.py init_setup --application_config <your_application_config_file_path>
```

- This command generates an intermediate application configuration with suggested plugins and saves it as `application_config_with_plugins.json` in the `workdir` directory.  
- You can refer to a sample configuration file here: [application_config.json](paig_evaluation/application_config.json).

---

#### 2. Generate Setup Config

To generate a setup configuration, use:  
```bash
python __main__.py setup
```

- This command outputs the setup configuration to the console using the generated `application_config_with_plugins.json` file.

---

#### 3. Save the Setup Config

Copy the setup configuration from the console output and save it into a JSON file.  

---

#### 4. Run the Evaluation

Run the evaluation using the following command:  
```bash
python __main__.py run --paig_eval_config <your_config_json_file_path>
```

- This command executes the evaluation and outputs the results in JSON format on the console.  

---

## Example Workflow

1. Create the intermediate application configuration:  
   ```bash
   python __main__.py init_setup --application_config application_config.json
   ```
2. Generate the setup configuration:  
   ```bash
   python __main__.py setup
   ```
3. Save the setup configuration to a JSON file (e.g., `setup_config.json`).  
4. Run the evaluation:  
   ```bash
   python __main__.py run --paig_eval_config setup_config.json
   ```

The evaluation report will be displayed in JSON format on the console.
