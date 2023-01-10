#!/usr/bin/env python3

# Copyright 2022 Google Sans Project Authors

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import os
import yaml
from pathlib import Path


def main():
    try:
        tag_name = os.environ["GITHUB_REF"].replace("refs/tags/", "")
        workspace = Path(os.environ["GITHUB_WORKSPACE"])
        config_path = workspace / "sources" / "config.yaml"
        file_text = config_path.read_text()
    except (KeyError, FileNotFoundError) as e:
        print(e)
        print("This script is intended to be run by CI during a release. Exiting")
        exit(2)

    gftools_config = yaml.safe_load(file_text)
    for source in gftools_config["sources"]:
        print(f"Bumping {source} to {tag_name}")
        cmd = subprocess.run(
            f"bumpfontversion sources/{source} --new-version {tag_name}",
            shell=True,
            capture_output=True,
            text=True,
        )
        if cmd.returncode != 0:
            print("bumpfontversion failed!")
            print(cmd.stderr)
            exit(1)


if __name__ == "__main__":
    main()
