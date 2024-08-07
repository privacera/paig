import configparser
import os

path_append = ""
if os.getenv('PAIG_ROOT_DIR'):
    path_append = os.getenv('PAIG_ROOT_DIR') + '/'

config = configparser.ConfigParser()
config.read(f'{path_append}core/exceptions/error-messages.properties')


def get_error_message(key, *args):
    try:
        message = config.get('errors', key)
    except configparser.NoOptionError:
        message = config.get('errors', 'error_something_went_wrong',
                                  fallback="Something went wrong. Please try again later. If the error persists, "
                                           "then contact Privacera Support.")
    return message.format(*args)


ERROR_RESOURCE_NOT_FOUND = "error_resource_not_found"
ERROR_RESOURCE_ALREADY_EXISTS = "error_resource_already_exists"
ERROR_FIELD_REQUIRED = "error_field_required"
ERROR_FIELD_LENGTH_EXCEEDS = "error_field_length_exceeds"
ERROR_FIELD_INVALID = "error_field_invalid"
ERROR_INVALID_STATUS = "error_invalid_status"
ERROR_FIELD_VALUE_INVALID = "error_field_value_invalid"
ERROR_FIELD_CANNOT_BE_UPDATED = "error_field_cannot_be_updated"
ERROR_ALLOWED_VALUES = "error_allowed_values"
ERROR_INVALID_PERMISSION_PUBLIC_ALLOWED = "error_invalid_permission_public_allowed"
ERROR_INVALID_PERMISSION_PUBLIC_DENIED = "error_invalid_permission_public_denied"
ERROR_SAME_ACTORS_IN_ALLOWED_DENIED = "error_same_actors_in_allowed_denied"
ERROR_RESOURCE_IN_USE = "error_resource_in_use"
ERROR_SOMETHING_WENT_WRONG = "error_something_went_wrong"
ERROR_ENCRYPTION_MASTER_KEY_NOT_FOUND = "error_encryption_master_key_not_found"