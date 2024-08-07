# PAIG Opensource
PAIG offers tools designed to enhance the security and compliance of your AI applications. Whether you're using chatbots internally, incorporating AI services into your products, or utilizing automated tools to process tasks like customer support tickets or feedback, PAIG ensures that you maintain the highest standards of security and adherence to compliance. It's tailored for businesses that value a robust yet straightforward approach to AI application governance. 
## Contents
- [Overview](#overview)
- [Technology Stack](#technology-stack)
- [Configuration](#configuration)
- [How to Start Development Server](backend/paig/README.md)
- [How to Start/Build Web UI](frontend/README.md)
- [How to Setup Database](#databsesetup)
- [Privacera PAIG as a Python library](backend/README.md)
- [Contributing to PAIG](#contributing)



## Overview <a name="overview"></a>
PAIG provides a platform for AI governance. It allows users to governance and audits the data on one platform. PAIG uses multiple services to provide the governance and audits.

## Technology Stack <a name="technology-stack"></a>
PAIG is a web based application. It uses the following technologies:
* **Web Application Framework:** ReactJS
* **Backend:** FastAPI (Python)
* **Database:** Configured by the user


## Configuration <a name="configuration"></a>
PAIG provides overlay configuration. PAIG will use the default configuration provided in the default_config.yaml file.
This default configuration can be overridden by the user-provided custom configuration.
The user can provide the custom configuration in the following ways:
1. Create a new custom configuration file in the custom folder that is provided to the application.
2. The naming convention for the custom configuration file should be as follows:
   ```bash
   <ENVIRONMENT_NAME>_config.yaml
   ```
   For example:
   ```bash
   dev_config.yaml
   ```
   _Note-_ ENVIRONMENT_NAME is also referred to as PAIG_DEPLOYMENT in the application.
3. In a custom configuration file, the user should provide new configuration key values or override the existing configuration.

## How to Setup Database <a name="databsesetup"></a>
User will have to create/update the tables in the database manually. Please refer to  Database for more details.
[How to setup database](backend/paig/alembic_db/README.md)

## Contributing to PAIG <a name="contributing"></a>
All contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome.
A detailed overview on how to contribute can be found in the [contributing guide](docs/CONTRIBUTING.md).
<br>As contributors and maintainers to this project, you are expected to abide by `PAIG` code of conduct. More information can be found at [code of conduct](docs/CODE_OF_CONDUCT.md).

