#!/bin/sh

# Check repo is mounted
[[ -d /github/workspace/.git ]] || echo "ERROR: repository not found at /github/workspace"
[[ -d /github/workspace/.git ]] || exit 1

# An error is thrown about using the repo as configured by actions/checkout otherwise
git config --global --add safe.directory /github/workspace

# Change to repo location as otherwise ufodiff dies
cd /github/workspace

# Re-parse branch from 3rd arg, which will be branch:name (see action.yml)
branch=$(echo $3 | cut -d : -f 2)
git fetch origin "$branch" &> /dev/null
git branch "$branch" "origin/$branch" &> /dev/null

# Call ufodiff with the supplied args
ufodiff $*
