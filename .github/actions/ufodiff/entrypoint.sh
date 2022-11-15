#!/bin/sh

# Check repo is mounted
[[ -d /github/workspace/.git ]] || echo "ERROR: repository not found at /github/workspace"
[[ -d /github/workspace/.git ]] || exit 1

# An error is thrown about using the repo as configured by actions/checkout otherwise
git config --global --add safe.directory /github/workspace

# Change to repo location as otherwise ufodiff dies
cd /github/workspace

git fetch origin main
git branch main origin/main

# Call ufodiff with the supplied args
ufodiff $*
