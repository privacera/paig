#!/bin/bash

set -x
IMG=paig-securechat
TAG=latest

while getopts h:i:t:e: flag
do
    case "${flag}" in
        h) DOCKER_HUB=${OPTARG};;
        i) DOCKER_IMG=${OPTARG};;
        t) DOCKER_TAG=${OPTARG};;
        e) EXTRA_OPTS=${OPTARG};;
        *) echo "Invalid option: -$flag" >&2
           exit 1
           ;;
    esac
done

if [ -z "${DOCKER_HUB}" ]; then
  DOCKER_HUB=$HUB
fi

if [ -z "${DOCKER_TAG}" ]; then
  DOCKER_TAG=$TAG
fi

if [ -z "${DOCKER_IMG}" ]; then
  DOCKER_IMG=${IMG}
fi

if [ -z "${DOCKER_HUB}" ]; then
  DOCKER_NAME_TAG="$DOCKER_IMG:$DOCKER_TAG"
else
  DOCKER_NAME_TAG="$DOCKER_HUB/$DOCKER_IMG:$DOCKER_TAG"
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"
cd ..

docker build \
  --file ./docker/Dockerfile \
  --progress plain \
  --no-cache \
  --rm \
  -t "${DOCKER_NAME_TAG}" .
