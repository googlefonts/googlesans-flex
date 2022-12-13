#!/bin/sh
# Copyright 2022 Google Sans Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Check repo is mounted
if [ ! -e /github/workspace/.git ] ; then
    echo "ERROR: repository not found at /github/workspace"
    exit 1
fi

# An error is thrown about using the repo as configured by actions/checkout otherwise
git config --global --add safe.directory /github/workspace

# Change to repo location as otherwise ufodiff dies
# shellcheck disable=SC2164
cd /github/workspace

# Re-parse branch from 3rd arg, which will be branch:name (see action.yml)
branch=$(echo "$3" | cut -d : -f 2)
git fetch origin "$branch" >/dev/null 2>&1
git branch "$branch" "origin/$branch" >/dev/null 2>&1

# Call ufodiff with the supplied args
ufodiff "$*"
