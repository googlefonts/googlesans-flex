#!/bin/sh
set -e

# Check branches are mounted
if [ ! -d /github/workspace/main ]; then
    echo "ERROR: Missing branch to merge into (destination branch)"
    exit 1
fi
if [ ! -d /github/workspace/staging ]; then
    echo "ERROR: Missing branch to merge (source branch)"
    exit 1
fi

echo "Merging designspaces..."
python3 /scripts/gs-merge-designspace.py \
    --source /github/workspace/staging/sources/GoogleSansFlex.designspace \
    --target /github/workspace/main/sources/GoogleSansFlex.designspace
echo

echo "Normalising designspaces..."
python3 /scripts/gs-normalize-designspace.py \
    --source-dir /github/workspace/main/sources
