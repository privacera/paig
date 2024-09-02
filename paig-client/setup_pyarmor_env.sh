#!/bin/bash

$(aws secretsmanager get-secret-value --secret-id 'paig-ops-sre-secrets' \
| jq -r '.SecretString | fromjson | keys[] as $k | "export \($k)=\(.[$k])"')

echo $PYARMOR_KEY | base64 --decode  > pyarmor-key.zip
ls -la pyarmor-key.zip
md5sum pyarmor-key.zip

# Assume the dev role and get temporary credentials
TEMP_ROLE=$(aws sts assume-role --role-arn "arn:aws:iam::404161567776:role/paig-dev-tf-role" --role-session-name "AssumedRoleSession")

# Export the temporary credentials
export AWS_ACCESS_KEY_ID=$(echo $TEMP_ROLE | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $TEMP_ROLE | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $TEMP_ROLE | jq -r '.Credentials.SessionToken')

