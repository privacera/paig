# PAIG
PAIG offers tools designed to enhance the security and compliance of your AI applications. Whether you're using chatbots internally, incorporating AI services into your products, or utilizing automated tools to process tasks like customer support tickets or feedback, PAIG ensures that you maintain the highest standards of security and adherence to compliance. It's tailored for businesses that value a robust yet straight forward approach to AI application governance

## Contents
- [Installation](#Installation)
- [Usage](#usage)
- [PAIG Server Background Mode](#backgroundmode)
- [Optional Configuration](#configuration)


## Installation <a name="Installation"></a>
PAIG is a python library which can be installed using pip.

```shell
pip install paig-server
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
    paig run --port 4545 --host 0.0.0.0 --background true
    ```

2. **Run as an Embedded Service:** 
<br>You can run PAIG in background by importing the library in your Python code. 
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


## Optional Configuration <a name="configuration"></a>
PAIG provides overlay configuration. You can provide the custom configuration in the following ways:
1. Create a new directory in the present working directory of the project with the name custom-conf.
2. Create a new custom configuration file named `<env>_config.yaml`(e.g. dev_config.yaml) in the custom-conf folder which will override default_config.yaml.
3. In a custom configuration file, the user should provide new configuration key values or override the existing configuration.
<br>Example: `custom-conf/dev_config.yaml`

    ```yaml
    database:
      url: "sqlite+aiosqlite:///db/database.db"
    
    security:
      basic_auth:
        secret: "<your_secret>"
    ```
