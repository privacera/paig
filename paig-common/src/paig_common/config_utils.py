import logging
from jproperties import Properties

logger = logging.getLogger(__name__)

configs_properties = Properties()


# You can load multiple config files, but order matters. The latest one will overwrite any
# properties defined by previous config files
def load_config_file(config_file_path):
    print(f"Loading config file {config_file_path}")
    logger.info(f"Loading config file {config_file_path}")
    with open(config_file_path, 'rb') as config_file:
        configs_properties.load(config_file)


def get_property_value(property_name, default_value=None):
    property_value = configs_properties.get(property_name)
    if property_value and property_value.data:
        return property_value.data
    return default_value


def get_property_value_list(property_name, default_value=None):
    value = get_property_value(property_name, default_value)
    try:
        return value.split(",")
    except Exception as e:
        logger.error(f"The property '{property_name}' with value '{value}' and default value '{default_value}' cannot "
                     f"be converted to list. Error: {e}")
        return None


def get_property_value_int(property_name, default_value=None):
    value = get_property_value(property_name, default_value)
    if not value:
        return default_value

    try:
        # Try to convert it to an integer and return
        return int(value)
    except ValueError:
        logger.error(f"The property '{property_name}' with value '{value}' cannot be converted to an integer.")
        return default_value


def get_property_value_float(property_name, default_value=None):
    value = get_property_value(property_name, default_value)
    if not value:
        return default_value
    try:
        # Try to convert it to an integer and return
        return float(value)
    except ValueError:
        logger.error(f"The property '{property_name}' with value '{value}' cannot be converted to float.")
        return default_value


def get_property_value_boolean(property_name, default_value=None):
    value = get_property_value(property_name, default_value)
    if not value:
        return default_value

    try:
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ['true']
        else:
            return default_value
    except ValueError:
        logger.error(f"The property '{property_name}' with value '{value}' cannot be converted to boolean.")
        return default_value


def get_keys():
    return configs_properties.keys()
