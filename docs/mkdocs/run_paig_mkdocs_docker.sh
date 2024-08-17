#!/bin/bash
set -e
set -x
PORT=8006
CONTAINER_NAME=mkdir-${PORT}
MKDOCS_IMAGE=privacera/paig-mkdocs:latest
#MKDOCS_IMAGE=privacera-mkdocs-materials-custom

PORT_MAPPING="-p $PORT:$PORT"
DOCKER_ENV=
IS_BUILD=false
if [ "$1" == "build" ]; then
  DOCKER_ENV="$DOCKER_ENV -e CI=true"
  PORT_MAPPING=""
  IS_BUILD=true
elif [ "$1" == "" ]; then
  #https://www.mkdocs.org/user-guide/cli/#mkdocs-serve
  params="serve --dev-addr=0.0.0.0:$PORT --dirty"
fi


git_home=$(git rev-parse --show-toplevel)
docs_folder="$script_folder"

docker rm -f ${CONTAINER_NAME} || true
docker run --rm -v "${git_home}:/git_home" $DOCKER_ENV $PORT_MAPPING --name ${CONTAINER_NAME} -w /git_home/docs/mkdocs $MKDOCS_IMAGE $params $*

#docker run --rm -v "${docs_folder}:/docs" $DOCKER_ENV $PORT_MAPPING --name ${CONTAINER_NAME} $MKDOCS_IMAGE $params $*
# Get the script folder
#script_folder="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
