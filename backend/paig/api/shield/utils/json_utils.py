import json


def mask_json_fields(request_obj, fields_to_mask, mask_value="*****"):
    """
    Masks specified fields in a JSON string with a given mask value.

    Args:
        request_obj (str): A JSON-formatted string representing the data to be masked.
        fields_to_mask (list of str): A list of field names (keys) that should be masked.
        mask_value (str): The value to use as a mask. Defaults to "*****".

    Returns:
        str: A JSON-formatted string with the specified fields masked.
   """
    def recursive_mask(request_data):
        if isinstance(request_data, dict):
            for key, value in request_data.items():
                if key in fields_to_mask:
                    request_data[key] = mask_value
                elif isinstance(value, (dict, list)):
                    recursive_mask(value)
        elif isinstance(request_data, list):
            for item in request_data:
                recursive_mask(item)

    # Parse the JSON data
    data = json.loads(request_obj)

    # Mask the specified fields
    recursive_mask(data)

    # Serialize the JSON back to a string
    masked_json = json.dumps(data)
    return masked_json
