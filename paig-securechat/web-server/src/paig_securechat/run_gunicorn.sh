#!/bin/bash
SECURE_CHAT_DEPLOYMENT="dev"
CONFIG_PATH="configs"
EXT_CONFIG_PATH="custom-configs"
PORT=3535
HOST=0.0.0.0
usage() { echo "Usage: $0 [-e <string>] [-c <string>] [-h <string>] [-p <integer>]" 1>&2; exit 1; }

while getopts ":e:c:p:h:" opt; do
    case $opt in
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

echo "SECURE_CHAT_DEPLOYMENT = ${SECURE_CHAT_DEPLOYMENT}"
echo "CONFIG_PATH = ${CONFIG_PATH}"
echo "PORT = ${PORT}"
echo "HOST = ${HOST}"
echo "EXT_CONFIG_PATH = ${EXT_CONFIG_PATH}"



gunicorn "app.server:app" \
          --access-logfile="-"  \
          -e SECURE_CHAT_DEPLOYMENT="${SECURE_CHAT_DEPLOYMENT}" \
          -e CONFIG_PATH="${CONFIG_PATH}" \
          -e EXT_CONFIG_PATH="${EXT_CONFIG_PATH}" \
          --bind ${HOST}:${PORT} \
          -w 4  -k uvicorn.workers.UvicornWorker --preload


