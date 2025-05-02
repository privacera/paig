#!/bin/bash

# Clean any previous core/conf
rm -rf paig_eval_service/core paig_eval_service/conf

# Copy real folders
cp -r ../../core paig_eval_service/core
cp -r ../../conf paig_eval_service/conf

# Build the wheel
python -m build -w

# Clean up if needed
rm -rf paig_eval_service/core paig_eval_service/conf paig_eval_service.egg-info build
