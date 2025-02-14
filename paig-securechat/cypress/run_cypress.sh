#!/bin/bash

# Bring up Docker containers
docker-compose -f ../docker/docker-compose.yml up -d

# Check the exit status
if [ $? != 0 ]; then
    echo "Secure Chat Start failed"
    exit $?
fi

echo "Secure Chat Starting, sleeping for 30 seconds"
# Wait for app to start
sleep 30

echo "Running Cypress tests"

# Run Cypress tests
npx cypress run

docker-compose -f ../docker/docker-compose.yml down

# Use this command to run Cypress GUI/Chrome
# npx cypress open
