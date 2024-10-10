#!/bin/bash
SECURE_CHAT_DEPLOYMENT="dev"
CONFIG_PATH="configs"
EXT_CONFIG_PATH="custom-configs"
usage() { echo "Usage: $0 [-e <string>] [-c <string>]" 1>&2; exit 1; }

while getopts ":e:c:" opt; do
    case $opt in
        e)
            e=${OPTARG}
            SECURE_CHAT_DEPLOYMENT=${e}
            ;;
        c)
            c=${OPTARG}
            CONFIG_PATH=${c}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))
echo "Setting up database"
echo "SECURE_CHAT_DEPLOYMENT = ${SECURE_CHAT_DEPLOYMENT}"
echo "CONFIG_PATH = ${CONFIG_PATH}"
echo "EXT_CONFIG_PATH = ${EXT_CONFIG_PATH}"

export SECURE_CHAT_DEPLOYMENT="${SECURE_CHAT_DEPLOYMENT}"
export CONFIG_PATH="${CONFIG_PATH}"
export EXT_CONFIG_PATH="${EXT_CONFIG_PATH}"

echo "create/apply migration to database"
alembic -c database_setup/alembic.ini upgrade head
