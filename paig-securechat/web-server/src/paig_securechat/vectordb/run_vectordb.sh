#!/bin/bash

# Check if the number of arguments is correct
if [ "$1" -eq 1 ]; then
    file_path=$1
    python vectordb_standalone.py "$file_path"
elif [ "$#" -eq 2 ]; then
    file_path=$1
    cleanup=$2
    python vectordb_standalone.py "$file_path" "$cleanup"
else
    python vectordb_standalone.py
fi