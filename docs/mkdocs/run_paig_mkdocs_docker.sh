#!/bin/bash
set -e
set -x
PORT=8006
CONTAINER_NAME=mkdir-${PORT}

PORT_MAPPING="-p $PORT:$PORT"
DOCKER_ENV=
if [ "$1" == "build" ]; then
  DOCKER_ENV="$DOCKER_ENV -e CI=true"
  PORT_MAPPING=""
elif [ "$1" == "" ]; then
  #https://www.mkdocs.org/user-guide/cli/#mkdocs-serve
  params="serve --dev-addr=0.0.0.0:$PORT --dirty"
fi

# Get the script folder
script_folder="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

docs_folder="$script_folder"

MKDOCS_IMAGE=privacera/paig-mkdocs:latest
docker rm -f ${CONTAINER_NAME} || true
docker run --rm -v "${docs_folder}:/docs" $DOCKER_ENV $PORT_MAPPING --name ${CONTAINER_NAME} $MKDOCS_IMAGE $params $*
