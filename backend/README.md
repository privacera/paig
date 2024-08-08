# PAIG Opensource
PAIG is a web application that provides a platform for AI governance and audits that data. 

## Contents
- [Installation](#Installation)
- [Usage](#usage)
- [Configuration](#configuration)


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
