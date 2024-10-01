#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "${SCRIPT_DIR}"
cd ..

ROOT_DIR=$(pwd)

# Set the directories
REACT_APP_DIR="$ROOT_DIR/frontend/webapp"
FASTAPI_APP_DIR="$ROOT_DIR/backend/paig"
FASTAPI_STATIC_DIR="$FASTAPI_APP_DIR/templates"

# Navigate to the React app directory
cd $REACT_APP_DIR

# Install dependencies and build the React app
echo "Installing React dependencies..."
npm install

echo "Building React app..."
npm run build

# Remove old static files in the FastAPI project
echo "Cleaning old static files in FastAPI project..."
rm -rf $FASTAPI_STATIC_DIR/*

# Copy the new build files to the FastAPI static directory
echo "Copying new build files to FastAPI project..."
mv public/styles/fonts  public/static/styles && rm -rf public/styles && cp -r public/* $FASTAPI_STATIC_DIR/

# Cleanup public directory
echo "Cleaning old static files in FastAPI project..."
rm -rf public

echo "Build and copy process completed successfully."

# Navigate back to the original directory
cd $ROOT_DIR
