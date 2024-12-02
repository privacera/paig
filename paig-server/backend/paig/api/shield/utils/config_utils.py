import logging

from jproperties import Properties

from core.utils import format_to_root_path

logger = logging.getLogger(__file__)

configs_properties = Properties()


# You can load multiple config files, but order matters. The latest one will overwrite any
# properties defined by previous config files
def load_config_file(config_file_path):
    """
    Loads properties from the specified configuration file.

    The latest file loaded will overwrite any properties defined by previously loaded files.
    """
    print(f"Loading config file {config_file_path}")
    logger.info(f"Loading config file {config_file_path}")
    with open(config_file_path, 'rb') as config_file:
        configs_properties.load(config_file)


def get_property_value(property_name, default_value=None):
    """
    Retrieves the value of the specified property as a string.

    Returns:
        str: The value of the property, or the default value if the property is not found.
    """
    property_value = configs_properties.get(property_name)
    if property_value and property_value.data:
        return property_value.data
    return default_value


def get_property_value_list(property_name, default_value=None):
    """
    Retrieves the value of the specified property and splits it into a list of strings.

    Returns:
        list: The list of strings from the property value, or the default value if conversion fails.
    """
    value = get_property_value(property_name, default_value)
    try:
        if isinstance(value, list):
            return value
        elif "," in value:
            return value.split(",")
        else:
            return [value]
    except Exception as e:
        logger.error(f"The property '{property_name}' with value '{value}' and default value '{default_value}' cannot "
                     f"be converted to list. Error: {e}")
        return default_value if default_value is not None else []


def get_property_value_int(property_name, default_value=None):
    """
     Retrieves the value of the specified property and converts it to an integer.

     Returns:
         int: The integer value of the property, or the default value if conversion fails.
     """
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
    """
    Retrieves the value of the specified property and converts it to a float.

    Returns:
        float: The float value of the property, or the default value if conversion fails.
    """
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
    """
    Retrieves the value of the specified property and converts it to a boolean.

    Returns:
        bool: The boolean value of the property, or the default value if conversion fails.
    """
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
    """
    Returns a view of all property names (keys) currently loaded from the properties files.

    Returns:
        dict_keys: A view of the property names.
    """
    return configs_properties.keys()


def load_shield_configs():
    load_config_file(format_to_root_path("api/shield/conf/default_configs.properties"))
    load_config_file(format_to_root_path("api/shield/conf/local_configs.properties"))
