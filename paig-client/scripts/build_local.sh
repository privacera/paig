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

pwd=`pwd`
rm -rf ${SCRIPT_DIR}/dist
cd ${SCRIPT_DIR}/plugin
python3 -m build
ls -la dist
cd $pwd
