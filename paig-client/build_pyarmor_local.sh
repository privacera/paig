#!/bin/bash

set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DIST_PYARMOR_DIR=${SCRIPT_DIR}/dist_pyarmor
pwd=`pwd`

rm -rf ${DIST_PYARMOR_DIR}

mkdir -p ${DIST_PYARMOR_DIR}/src
pyarmor gen -O ${DIST_PYARMOR_DIR}/src -i ${SCRIPT_DIR}/plugin/src/privacera_shield
cp ${SCRIPT_DIR}/plugin/{LICENSE,README.md,pyproject.toml,privacera_version.txt}  ${DIST_PYARMOR_DIR}

cd ${DIST_PYARMOR_DIR}
python3 -m build
ls -la ${DIST_PYARMOR_DIR}/dist
cd $pwd
