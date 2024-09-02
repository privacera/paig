import re
import json
import boto3
import gitlab
import os


# Function to get the GitLab access token from Secrets Manager
def get_gitlab_access_token(secret_name):
    print(f"Getting GitLab access token from Secrets Manager for secret {secret_name}")
    try:
        secret_string = _secrets_manager.get_secret_value(SecretId=secret_name)
        secret_data = json.loads(secret_string['SecretString'])
        return secret_data.get('paig_shield_common')
    except Exception as ex:
        print(f"Error retrieving GitLab access token from Secrets Manager: {ex}")
        exit(1)


def update_version(filename, version, version_update_type):
    print(f"Updating version in file '{filename}'...")

    # Extract version components
    major, minor, patch = map(int, version.split('.'))

    # Increment patch and handle overflow to minor and major versions
    version_updates = {
        'patch': (lambda p, mi, ma: (p + 1, mi, ma)),
        'minor': (lambda p, mi, ma: (0, mi + 1, ma)),
        'major': (lambda p, mi, ma: (0, 0, ma + 1)),
    }

    update_func = version_updates.get(version_update_type, (lambda m, mi, ma: (m, mi, ma)))  # Default function
    _patch, _minor, _major = update_func(patch, minor, major)  # Call the function and unpack
    # Construct the new version
    return f"version={_major}.{_minor}.{_patch}"


def read_version(filename):
    print(f"Reading version from file '{filename}'...")
    try:
        with open(filename, 'r') as f:
            version_line = f.readline().strip()
            # Validate version format
            match = re.match(r'^version=([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$', version_line)
            if not match:
                raise ValueError(f"Invalid version format in '{filename}'. version format expect is "
                                 f"'version=MAJOR.MINOR.PATCH'")
            version = version_line.split('=')[1]
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found.")
    except Exception as ex:
        raise Exception(f"Error reading version from '{filename}': {ex}")
    return version


def write_version(filename, line):
    try:
        file = project.files.get(filename, ref=_target_brn)
        file.content = line
        file.save(branch=_target_brn, commit_message=f'PAIG-0000 Update version file to {line}')
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found.")
    except Exception as ex:
        raise Exception(f"Error writing version to '{filename}': {ex}")


# ###########################PROGRAM START######################################
_version_update_type = os.getenv('VERSION_UPDATE_TYPE')
print(f"Starting upgrade for release version...")
print(f"Version update type: {_version_update_type}")

# Set the AWS region and secret name
AWS_REGION = 'us-east-1'
SECRET_NAME = 'gitlab-runner/dev'

# Initialize the AWS Secrets Manager client
_secrets_manager = boto3.client('secretsmanager', region_name=AWS_REGION)
_gitlab_access_token = get_gitlab_access_token(SECRET_NAME)
print(f"GitLab access token: {_gitlab_access_token}")

# Example usage
_file = "current_version.txt"
_gitlab_url = "https://gitlab.com"
_project_name_with_namespace = "privacera/paig/shield-common"
_gl = None
_project = None
try:
    gl = gitlab.Gitlab(_gitlab_url, private_token=_gitlab_access_token)
    project = gl.projects.get(_project_name_with_namespace)
except Exception as e:
    print(f"Error while creating gitlab object: {e}")
    exit(1)

_version = None
_target_brn = os.getenv('CI_COMMIT_REF_NAME')
try:
    _version = read_version(_file)
    print(f"Current version: {_version}")

    _tag = project.tags.create({'tag_name': _version, 'ref': _target_brn})
    print(f"Tag created: {_tag} : {_version} on main branch")
except Exception as e:
    print(f"Error: {e}")
    exit(1)

try:
    _new_version = update_version(_file, _version, _version_update_type)
    print(f"Saving new version: {_new_version}")
    write_version(_file, _new_version)
except (FileNotFoundError, ValueError) as e:
    print(f"Error: {e}")
    exit(1)
