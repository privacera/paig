#!/bin/bash

set -euxo pipefail

cd $(dirname $0)

python3 -m venv venv
source venv/bin/activate

pip3 install --upgrade pip
pip3 install -r requirements.txt
ret=$?
if [ $ret -ne 0 ]; then
  echo "ERROR installing python packages. ret=$ret"
  exit $ret
fi