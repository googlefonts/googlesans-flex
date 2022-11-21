#!/bin/sh

# Check branches are mounted
if [ ! -d /github/workspace/main ]; then
    echo "ERROR: Missing branch to merge into (destination branch)"
    exit 1
fi
if [ ! -d /github/workspace/staging ]; then
    echo "ERROR: Missing branch to merge (source branch)"
    exit 1
fi

echo "Hello world!"

# TODO: run the actual Python scripts
