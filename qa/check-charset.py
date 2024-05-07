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
    "check_definitions": [Path(__file__).parent / "checks" / "charset.py"],
    "sections": {
        "Google Sans Custom Character Set Checks": [
            "com.google.fonts/check/googlesans/glyphs/glyphset-contents",
            # "com.google.fonts/check/googlesans/features/regression",  # TODO: For later
        ]
    },
    "exclude_checks": [
        "com.google.fonts/check/ftxvalidator_is_available",
        "com.google.fonts/check/dsig",
        "com.google.fonts/check/family/win_ascent_and_descent",  # replaced by custom checks
        "com.google.fonts/check/varfont/regular_opsz_coord",  # we want our opsz definition
    ]
}
