# Copyright 2020 Google Sans Authors

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


PROFILE = {
    "check_definitions": [Path(__file__).parent / "checks" / "googlesans.py"],
    "sections": {
        "Google Sans Flex Custom Checks": [
            "googlesansflex/opentype/os2/unicode_range_bits",
            "googlesansflex/opentype/head/created",
            "googlesansflex/vf/fvaraxes",
            "googlesansflex/vf/axis_names",
            "googlesansflex/vf/fvardefault",
            "googlesansflex/opentype/global_fu_attributes",
            "googlesansflex/android_ymin_ymax",
            "googlesansflex/android_hvar",
            "googlesansflex/varfont/has_HVAR",
            "googlesansflex/opentype/BASE",
        ],
        "Fontbakery checks": [
            "ots",
        ],
    },
}
