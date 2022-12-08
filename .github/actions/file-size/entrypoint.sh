#!/bin/sh

if [ ! -e /github/workspace/fonts ] ; then
    echo "ERROR: built fonts not found at /github/workspace/fonts"
    exit 1
fi

# shellcheck disable=SC2038
find /github/workspace/fonts -name '*.ttf' -type f | xargs python3 /report-filesize.py
