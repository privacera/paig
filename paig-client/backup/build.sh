#!/bin/bash 

set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TARGET_PATH=${SCRIPT_DIR}/plugin

# Removing old versions
rm -rf ${TARGET_PATH}/dist

version="0.1.0"
build_version=$(date +"%Y%m%d-%H-%M-%S")
cat <<END > ${TARGET_PATH}/privacera_version.txt
__version__ = "$version+$build_version"
END

echo "Setting env for using Code Artifact with pip"
export CODEARTIFACT_AUTH_TOKEN=$(aws codeartifact get-authorization-token --domain privacera-dev --domain-owner 587946681758 --region us-east-1 --query authorizationToken --output text)

pip config set global.index-url https://aws:$CODEARTIFACT_AUTH_TOKEN@privacera-dev-587946681758.d.codeartifact.us-east-1.amazonaws.com/pypi/pypi-store/simple/

echo "Installing build and twine tools"
python3 -m pip install --upgrade build twine virtualenv pip

echo "Doing the packaging build"
cd "$TARGET_PATH"
python3 -m build

echo "Contents of the dist folder"
ls -la dist

export TWINE_USERNAME=aws

export TWINE_PASSWORD=$(aws codeartifact get-authorization-token --domain privacera-dev --domain-owner 587946681758 --region us-east-1 --query authorizationToken --output text)

export TWINE_REPOSITORY_URL=$(aws codeartifact get-repository-endpoint --domain privacera-dev --domain-owner 587946681758 --repository pypi-store --region us-east-1 --format pypi --query repositoryEndpoint --output text)

echo "TWINE_REPOSTIORY_URL=$TWINE_REPOSITORY_URL"

python3 -m twine upload --repository codeartifact dist/*

