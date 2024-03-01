#!/usr/bin/env bash

# Copyright 2024 Google Sans Project Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This files makes any changes necessary to the GitHub workflows required for
# you to be able to start devving on them in the playground repo. They're all
# done in a single commit that you can rebase & drop later when ready to PR

# If you're testing this script and want to undo, run:
# git reset -q HEAD^ && git restore .github/workflows

# Change runners to free ones
sed -i 's|\[linux, googlefonts-64cores-256GB\]|ubuntu-latest|g' \
    .github/workflows/*.{yml,yaml}

# Change timeouts to 60 minutes across the board
sed -i -E 's|timeout-minutes: [0-9]+|timeout-minutes: 60|g' \
    .github/workflows/*.{yml,yaml}

# Change callable workflow repository
sed -i 's|uses: googlefonts/googlesans-flex|uses: daltonmaag/googlesans-flex-playground|g' \
    .github/workflows/*.{yml,yaml}

git commit -m "Patchie" .github/workflows
