#!/bin/bash
set -ex


SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
cd ..



docker-compose \
  -f docker/docker-compose.yml \
  up

