# Quick Start PAIG
PAIG provides platform to secure and govern your AI applications.

## Contents
- [Installation](#Installation)
- [Usage](#usage)
- [PAIG Server Background Mode](#backgroundmode)
- [How To Govern Your LLM Interaction](SNIPPET_USING_PLUGIN.md)
- [Optional Configuration](#configuration)
- [Try Out Using Notebook](#notebooks)


## Installation <a name="Installation"></a>
PAIG is a python library which can be installed using pip.

```shell
pip install paig
python -m spacy download en_core_web_lg
```

## Usage <a name="usage"></a>
PAIG  can be used in following ways:
1. **Run as a service:** 
   <br>You can simply run the PAIG as a service by running following command:
    
   ```shell
    paig run
    ```
   
    To get the help for the command and see all available [OPTIONS], you can run the following command:
    
   ```shell
    paig --help
    ```
   
    Example:
    ```shell
    paig run --port 4545 --host 127.0.0.1
    ```
   
    **Note:** *Admin user credentials.*

   ```shell
   PAIG URL: http://127.0.0.1:4545
   username: admin
   password: welcome1
   ```
   
2. **Run as an Embedded Service:** You can run PAIG in background by importing the library in your Python code. 
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

## PAIG Server Background Mode <a name="backgroundmode"></a>
PAIG can be run in the background mode by setting the background flag to true.

1. To Start the PAIG in the background mode:
```bash
paig run --background true
```
**Note:** Please use help command to see all available options you can pass on command line.
```bash
paig --help
```
2. To Stop the PAIG Server:
```bash
paig stop
```
3. To Check the status of the PAIG Server:
```bash
paig status
```

## How To Govern Your LLM Interaction <a name="govern-your-llm"></a>
PAIG provides a platform to secure and govern your AI applications. You can use the PAIG to secure and govern your LLM interactions.
Try out this [code snippet](SNIPPET_USING_PLUGIN.md) to secure and govern your LLM interactions.

## Optional Configuration <a name="configuration"></a>
PAIG provides overlay configuration. You can provide the custom configuration in the following ways:
1. Create a new directory in the present working directory of the project with the name custom-conf.
2. Create a new custom configuration file named dev_config.yaml in the custom-conf folder that is provided to the application.
3. In a custom configuration file, the user should provide new configuration key values or override the existing configuration.
<br>Example: [custom-conf/dev_config.yaml](../backend/paig/conf/default_config.yaml)

## Try Out Using Notebooks <a name="configuration"></a>
This repository provides PAIG Notebooks to help you experiment with PAIG and integrate it with your LangChain applications. The notebook guides you through the setup and usage of PAIG, offering hands-on experience with its security and governance features.

### What You'll Learn

- **Application Setup**: Configure and initialize PAIG.
- **Running LLMChain**: Protect your prompts and responses using Privacera's security policies.
- **Access Control Handling**: See how Privacera intercepts and enforces policies in real-time.
- **Interactive Code Examples**: Follow along with code snippets and observe the immediate impact.

### How to run the notebook
1. **In Jupyter:-** Launch Jupyter Notebook from your local machine
   ```shell
      jupyter notebook
   ```
   Open the notebook named [PAIG_jupyter.ipynb](../notebooks/PAIG_jupyter.ipynb) from the file browser.

2. **In Google Colab:-** In Google Colab you can open the notebook named
[PAIG_colab.ipynb](../notebooks/PAIG_colab.ipynb)
   <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
   </a>
