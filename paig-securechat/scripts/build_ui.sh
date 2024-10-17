#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"
cd ..

ROOT_DIR=$(pwd)

# Set the directories
REACT_APP_DIR="$ROOT_DIR/web-ui"
FASTAPI_APP_DIR="$ROOT_DIR/web-server/src/paig_securechat"
FASTAPI_STATIC_DIR="$FASTAPI_APP_DIR/templates"
DATA_DIR="$ROOT_DIR/data"

echo "Remove existing data files from the package"
rm -rf $FASTAPI_APP_DIR/data/*
echo "Creating data folder"
mkdir -p $FASTAPI_APP_DIR/data
echo "Copying data files to the package"
cp -r  $DATA_DIR/* $FASTAPI_APP_DIR/data/

# Navigate to the React app directory
cd $REACT_APP_DIR

# Install dependencies and build the React app
echo "Installing React dependencies..."
npm install --legacy-peer-deps

echo "Building React app..."
npm run build

echo "Removing node_modules"
rm -rf node_modules

# Remove old static files in the FastAPI project
echo "Cleaning old static files in FastAPI project..."
rm -rf $FASTAPI_STATIC_DIR/*

echo "Creating templates folder"
mkdir -p $FASTAPI_STATIC_DIR

# Copy the new build files to the FastAPI static directory
echo "Copying new build files to FastAPI project..."
cp -r $REACT_APP_DIR/build/* $FASTAPI_STATIC_DIR/

# Remove build
echo "Removing node_modules"
rm -rf $REACT_APP_DIR/build

echo "Build and copy process completed successfully."

# Navigate back to the original directory
cd $ROOT_DIR