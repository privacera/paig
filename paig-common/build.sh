#!/bin/bash

set -x

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
TARGET_PATH=${SCRIPT_DIR}/src
DOMAIN_NAME="paig-dev"
DOMAIN_OWNER_ACCOUNT="404161567776"
REGION="us-east-1"

function create_privacera_version() {
  # Read the version from the file
  if [[ ! -f current_version.txt ]]; then
    echo "Error: File 'current_version.txt' does not exist."
    exit 1
  fi

  version=$(head -n 1 current_version.txt)

  # Validate the content format (starting with "version=")
  if [[ ! $version =~ ^version= ]]; then
    echo "Error: File content is not in the expected format (version=X.Y.Z)."
    exit 1
  fi

  # Extract the version number
  version="${version#version=}"

  # Validate format (X.Y.Z) using regex within the if block
  if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Error: Version format is invalid. It should be X.Y.Z (all integers)."
    exit 1
  fi

  if [ "$1" == "true" ]; then
    cat <<END >${TARGET_PATH}/privacera_version.txt
__version__ = "$version"
END
  else
    if [ -n "$CI_COMMIT_BRANCH" ]; then
      git_branch="$CI_COMMIT_BRANCH"
    else
      git_branch=$(git rev-parse --abbrev-ref HEAD)
    fi

    # remove all non-alphanumeric characters and convert to lowercase
    git_branch=$(echo "$git_branch" | tr -cd '[:alnum:]' | tr '[:upper:]' '[:lower:]')

    # if git_branch is main then append dev1 to version else append dev0 to the
    if [ "$git_branch" == "main" ]; then
      version="$version.dev1+$git_branch"
    else
      version="$version.dev0+$git_branch"
    fi

    build_num=$(date +"%Y%m%d.%H%M%S.%s")
    cat <<END >${TARGET_PATH}/privacera_version.txt
__version__ = "$version.$build_num"
END
   fi

   cat ${TARGET_PATH}/privacera_version.txt
}

function set_environment_vars() {
  echo "Setting env for using Code Artifact with pip"
  export CODEARTIFACT_AUTH_TOKEN=$(aws codeartifact get-authorization-token \
    --domain $DOMAIN_NAME \
    --domain-owner $DOMAIN_OWNER_ACCOUNT \
    --region $REGION \
    --query authorizationToken \
    --output text)

  export TWINE_USERNAME=aws
  export TWINE_PASSWORD=$CODEARTIFACT_AUTH_TOKEN
  export TWINE_REPOSITORY_URL=$(aws codeartifact get-repository-endpoint \
    --domain $DOMAIN_NAME \
    --domain-owner $DOMAIN_OWNER_ACCOUNT \
    --region $REGION \
    --repository pypi-store \
    --format pypi \
    --query repositoryEndpoint \
    --output text)
}

function do_pip_install() {
  echo "Installing build and twine tools"

  pip config set \
    global.index-url \
    https://aws:$CODEARTIFACT_AUTH_TOKEN@$DOMAIN_NAME-$DOMAIN_OWNER_ACCOUNT.d.codeartifact.$REGION.amazonaws.com/pypi/pypi-store/simple/

  python3 -m pip install --upgrade build twine virtualenv pip pyarmor python-gitlab boto3
}

function install_pyarmor_key() {
  echo "installing the pyarmor key"
  pyarmor reg pyarmor-key.zip
  pyarmor --version
}

function build_gitlab_pyarmor_all_platforms() {

  python_version=$(python3 -c "import platform;v=platform.python_version_tuple();print(f'cp{v[0]}{v[1]}')")
  declare -a platform=("windows.x86_64" "linux.x86_64" "darwin.x86_64" "darwin.aarch64")
  declare -a python_platform=("win_amd64" "linux_x86_64" "macosx_10_9_x86_64" "macosx_11_0_arm64")
  i=0
  for curr_platform in "${platform[@]}"; do
    echo "Platform: $curr_platform"

    DIST_PYARMOR_DIR=${SCRIPT_DIR}/dist_pyarmor_${curr_platform}
    rm -rf ${DIST_PYARMOR_DIR}
    mkdir -p ${DIST_PYARMOR_DIR}/src

    rm -rf .pyarmor

    pyarmor cfg trace_rft=1 enable_trace=1

    pyarmor gen \
      --enable-rft \
      --mix-str \
      --assert-import \
      --assert-call \
      --platform "$curr_platform" \
      -O ${DIST_PYARMOR_DIR}/src \
      -i src/privacera_shield_common

    find .pyarmor -ls
    grep trace.rft .pyarmor/pyarmor.trace.log
    grep trace.bcc .pyarmor/pyarmor.trace.log

    cd ${TARGET_PATH}
    cp {LICENSE,README.md,pyproject.toml,privacera_version.txt} ${DIST_PYARMOR_DIR}
    echo "Doing the packaging build for platform=${curr_platform}"
    cd ${DIST_PYARMOR_DIR}
    ls -ltRa
    python3 -m build -w
    echo "Contents of the dist folder"
    ls -la dist
    rename "${python_version}-${python_version}-${python_platform[$i]}"
    rm dist/*.tar.gz
    python3 -m twine upload --repository codeartifact dist/*
    cd ..
    ((i = i + 1))
  done
}

function rename() {
  pattern="dist/privacera-shield-common-*py3-none-any.whl"
  # Define the replacement string
  replacement="$1"

  # Loop through the files and rename them
  for file in $pattern; do
    new_name=$(echo "$file" | sed "s/py3-none-any/$replacement/")
    mv "$file" "$new_name"
  done
}

function build_gitlab_plain() {
  echo "Doing the packaging build without pyarmor"
  cd "$TARGET_PATH"
  ls -la
  cat privacera_version.txt
  python3 -m build -w
  echo "Contents of the dist folder"
  ls -la dist
  python3 -m twine upload --repository codeartifact dist/*
  if [ "$1" == "true" ]; then
    echo "Uploading to pypi DEBUG"
    upload_pypi
  fi
}

function build_local_plain() {
  build_tag=$(python3 adhoc/platform_tag.py)
  rm -rf ${SCRIPT_DIR}/src/dist
  cd ${SCRIPT_DIR}/src
  python3 -m build -w
  ls -la dist
  cd $SCRIPT_DIR
}

function upload_pypi() {
  pip config unset global.index-url
  export TWINE_USERNAME="__token__"
  export TWINE_PASSWORD="$PYPI_PASSWORD"
  echo "before TWINE_REPOSITORY_URL=$TWINE_REPOSITORY_URL"
  unset TWINE_REPOSITORY_URL
  echo "after TWINE_REPOSITORY_URL=$TWINE_REPOSITORY_URL"
  echo "python3 -m twine upload dist/* -u $TWINE_USERNAME -p $TWINE_PASSWORD --verbose"
  python3 -m twine upload dist/* -u $TWINE_USERNAME -p $TWINE_PASSWORD --verbose
}

function main() {

  if [ "$2" == "true" ]; then
    if [[ "$VERSION_UPDATE_TYPE" == "major" || "$VERSION_UPDATE_TYPE" == "minor" || "$VERSION_UPDATE_TYPE" == "patch" ]]; then
      echo "Version update type is $VERSION_UPDATE_TYPE"
    else
      echo "Invalid version update type $VERSION_UPDATE_TYPE. Valid values are major, minor, patch. Exiting."
      exit 1
    fi
  fi

  if [ "$1" == "gitlab-plain" ]; then
    echo "Building for gitlab plain"
    create_privacera_version "$2"
    set_environment_vars
    do_pip_install
    build_gitlab_plain "$2"
  elif [ "$1" == "gitlab-pyarmor" ]; then
    echo "Building for gitlab pyarmor"
    create_privacera_version "$2"
    set_environment_vars
    do_pip_install
    install_pyarmor_key
    build_gitlab_pyarmor_all_platforms "$2"
  else
    echo "Building local plain"
    create_privacera_version
    build_local_plain
  fi

  if [ "$2" == "true" ]; then
    cd $SCRIPT_DIR
    python3 upgrade_version.py
  fi
}

main "$@"
