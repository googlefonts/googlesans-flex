#!/usr/bin/env python3

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

from pathlib import Path


def main():
    for ufodir in Path("../sources/regular").glob("*.ufo"):
        fea_path = ufodir / "features.fea"
        if not fea_path.exists():
            with open(fea_path, "w") as f:
                f.write("include(family.fea);")
                print(f"Created {fea_path}.")

    for ufodir in Path("../sources/regular/ROND100").glob("*.ufo"):
        fea_path = ufodir / "features.fea"
        if not fea_path.exists():
            with open(fea_path, "w") as f:
                f.write("include(../family.fea);")
                print(f"Created {fea_path}.")


if __name__ == "__main__":
    main()
