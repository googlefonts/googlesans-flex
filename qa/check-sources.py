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
            "com.google.fonts/check/googlesansflex/sources/same_tabular_width",
            "com.google.fonts/check/googlesansflex/sources/suspicious_kerning_values",
            "com.google.fonts/check/googlesansflex/sources/same_kerning_groups",
            "com.google.fonts/check/googlesansflex/sources/kerning_present",
            "com.google.fonts/check/googlesansflex/sources/all_quadratics",
            "com.google.fonts/check/googlesansflex/sources/no_open_corners",
        ]
    },
}
