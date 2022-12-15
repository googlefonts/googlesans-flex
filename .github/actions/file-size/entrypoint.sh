#!/bin/sh

# If $1 is specified, use that as the path
if [ -n "$1" ] ; then
    REPO_PATH=$1
else
    REPO_PATH="/github/workspace"
fi

if [ ! -d "$REPO_PATH/fonts" ] ; then
    echo "ERROR: built fonts not found at $REPO_PATH/fonts"
    exit 1
fi

find "$REPO_PATH/fonts" -name '*.ttf' -type f -print0 | xargs -0 python3 /report-filesize.py
