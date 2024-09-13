# Copyright 2023 Google Sans Authors
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

from pathlib import Path

PROFILE = {
    "check_definitions": [Path(__file__).parent / "checks" / "sources.py"],
    "sections": {
        "Google Sans Flex Source Checks": [
            "googlesansflex/sources/same_tabular_width",
            "googlesansflex/sources/suspicious_kerning_values",
            "googlesansflex/sources/same_kerning_groups",
            "googlesansflex/sources/kerning_present",
            "googlesansflex/sources/all_quadratics",
            "googlesansflex/sources/no_open_corners",
            "googlesansflex/sources/decomposed_by_skip",
            "googlesansflex/sources/decomposed_by_mix",
            "googlesansflex/sources/decomposed_by_var_transform",
        ]
    },
}
