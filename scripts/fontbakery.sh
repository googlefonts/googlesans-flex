#!/usr/bin/env bash

# Copyright 2023 Google Sans Project Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script co-ordinates the running of all Fontbakery check profiles, and
# exiting non-zero if any of the suites failed. The name of the check profiles
# that failed are also printed

# Assumes the repository is in the parent folder of where the script lives
# Set env var SKIP_SOURCES if you don't want to check sources

set -e

all_ttfs="$(find fonts/ -name '*.ttf')"

# Switch to repo path by going to the parent folder of where this script is
cd "$(dirname "${BASH_SOURCE[0]}" | xargs dirname)"

# Setup venv with dependencies
[ -n "$GITHUB_RUN_ID" ] && echo "::group::Set up venv"
test -d venv_bakery || python3 -m venv venv_bakery
venv_bakery/bin/pip install -U setuptools wheel pip
# Install fontbakery on every run, isolated from build dependencies
if [ -e "requirements-fb.txt" ]; then
    echo "Using requirements-fb.txt"
    venv_bakery/bin/pip install -r requirements-fb.txt
else
    echo "Not pinning fontbakery"
    # fonttools[interpolatable] makes com.google.fonts/check/interpolation_issues around 5x faster
    venv_bakery/bin/pip install -U "fontbakery[googlefonts]" "fonttools[interpolatable]"
fi
[ -n "$GITHUB_RUN_ID" ] && echo "::endgroup::"
mkdir -p out/fontbakery

# All checks invocations are chained into `|| failed+=("test name")` so that:
# 1. we know if any of the tests failed
# 2. we don't immediately exit thanks to set -e
# 3. we can give a nice error message later
failed=()

# Source checks
if [ -z "$SKIP_SOURCES" ]; then
    find sources/ -name "*.ufo" -print0 | xargs -0 venv_bakery/bin/fontbakery \
        check-profile -l WARN --auto-jobs --succinct --no-progress \
        --html out/fontbakery/fontbakery-sources-report.html \
        qa/check-sources.py \
        sources/GoogleSansFlex.designspace \
        || failed+=("check-sources")
fi

# Compiled font tests
echo "$all_ttfs" \
    | xargs venv_bakery/bin/fontbakery check-profile -l WARN --auto-jobs --succinct --no-progress \
    --html out/fontbakery/fontbakery-outlines-report.html \
    fontbakery.profiles.outline {} \
    || failed+=("fontbakery.profiles.outline")

echo "$all_ttfs" \
    | xargs venv_bakery/bin/fontbakery check-profile -l WARN --auto-jobs --succinct --no-progress \
    --html out/fontbakery/fontbakery-googlesans-report.html \
    qa/check-googlesans.py {} \
    || failed+=("check-googlesans")

echo "$all_ttfs" \
    | xargs venv_bakery/bin/fontbakery check-profile -l WARN --auto-jobs --succinct --no-progress \
    --html out/fontbakery/fontbakery-fea-report.html \
    qa/check-fea.py {} \
    || failed+=("check-fea")

# NOTE: The following checks can be activated after the sources are stable:
# -venv_bakery/bin/fontbakery check-profile -l WARN --auto-jobs --succinct --html out/fontbakery/fontbakery-charset-report.html \
#	qa/check-charset.py fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf
# -venv_bakery/bin/fontbakery check-profile -l WARN --auto-jobs --succinct --html out/fontbakery/fontbakery-shaping-report.html \
#	qa/check-shaping.py fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf

if [[ ${#failed[@]} -gt 0 ]]; then
    # If on GitHub actions, make a posh GHA error
    [ -n "$GITHUB_RUN_ID" ] && echo -n "::error title=Fontbakery fails::"
    echo "The following Fontbakery profiles had fails/errors:" "${failed[@]}"
    exit 1
fi
