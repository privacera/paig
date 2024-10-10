#!/bin/bash
set -ex

SECURE_CHAT_DEPLOYMENT="dev"
CONFIG_PATH="configs"
PORT=3535
HOST=0.0.0.0
MODE="start"
usage() { echo "Usage: $0 [-m start|shell|bash] [-e <string>] [-c <string>] [-h <string>] [-p <integer>]" 1>&2; exit 1; }

while getopts ":m:e:c:p:h:" opt; do
    case $opt in
        m)
            m=${OPTARG}
            ((m == "start" || m == "shell" || m == "bash")) || usage
            MODE=${m}
            ;;
        e)
            e=${OPTARG}
            SECURE_CHAT_DEPLOYMENT=${e}
            ;;
        c)
            c=${OPTARG}
            CONFIG_PATH=${c}
            ;;
        p)
            p=${OPTARG}
            PORT=${p}
            ;;
        h)
            h=${OPTARG}
            HOST=${h}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))

set -eo pipefail
echo "paramters=<$*>"
echo "MODE = ${MODE}"
echo "SECURE_CHAT_DEPLOYMENT = ${SECURE_CHAT_DEPLOYMENT}"
echo "CONFIG_PATH = ${CONFIG_PATH}"
echo "HOST=${HOST}"
echo "PORT = ${PORT}"


source /venv/bin/activate
nginx
if [ "${MODE}" == "start" ]; then
    echo "Setting up database"
    ./run_db_setup.sh -e ${SECURE_CHAT_DEPLOYMENT} -c ${CONFIG_PATH} >> securechat/logs/db_setup.log 2>&1
    echo "starting gunicorn server"
    ./run_gunicorn.sh -e ${SECURE_CHAT_DEPLOYMENT} -c ${CONFIG_PATH} -p ${PORT} -h ${HOST}
elif [ "${MODE}" == "shell" ] || [ "${MODE}" == "bash" ]; then
    bash
else
    exec "$@"
fi