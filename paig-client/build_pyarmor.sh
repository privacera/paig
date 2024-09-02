#!/bin/bash 

set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
TARGET_PATH=${SCRIPT_DIR}/plugin
DIST_PYARMOR_DIR=${SCRIPT_DIR}/plugin/dist_pyarmor

# Removing old versions
rm -rf ${DIST_PYARMOR_DIR}

version="0.1.0"
build_version=$(date +"%Y%m%d-%H-%M-%S")
cat <<END > ${SCRIPT_DIR}/plugin/privacera_version.txt
__version__ = "$version+$build_version"
END

echo "Setting env for using Code Artifact with pip"
export CODEARTIFACT_AUTH_TOKEN=$(aws codeartifact get-authorization-token --domain privacera-dev --domain-owner 587946681758 --region us-east-1 --query authorizationToken --output text)

pip config set global.index-url https://aws:$CODEARTIFACT_AUTH_TOKEN@privacera-dev-587946681758.d.codeartifact.us-east-1.amazonaws.com/pypi/pypi-store/simple/

echo "Installing build and twine tools"
python3 -m pip install --upgrade build twine virtualenv pip pyarmor

echo "Doing the pyarmor build"
mkdir -p ${DIST_PYARMOR_DIR}/src
pyarmor gen -O ${DIST_PYARMOR_DIR}/src -i ${SCRIPT_DIR}/plugin/src/privacera_shield
cp ${SCRIPT_DIR}/plugin/{LICENSE,README.md,pyproject.toml,privacera_version.txt}  ${DIST_PYARMOR_DIR}

echo "Doing the packaging build"
cd ${DIST_PYARMOR_DIR}
python3 -m build

echo "Contents of the dist folder"
ls -la dist

export TWINE_USERNAME=aws

export TWINE_PASSWORD=$(aws codeartifact get-authorization-token --domain privacera-dev --domain-owner 587946681758 --region us-east-1 --query authorizationToken --output text)

export TWINE_REPOSITORY_URL=$(aws codeartifact get-repository-endpoint --domain privacera-dev --domain-owner 587946681758 --repository pypi-store --region us-east-1 --format pypi --query repositoryEndpoint --output text)

echo "TWINE_REPOSTIORY_URL=$TWINE_REPOSITORY_URL"

python3 -m twine upload --repository codeartifact dist/*
