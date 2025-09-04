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

import json
import subprocess
import tomllib
from pathlib import Path

from fontbakery.profiles.googlefonts import PROFILE as GOOGLEFONTS_PROFILE

# Try and exclude all checks that are covered by fontspector.
try:
    data_json = subprocess.check_output(
        ["fontspector", "--profile", "googlefonts", "--list-checks-json"]
    )
    data = json.loads(data_json)
    fontspector_checks = [check["id"] for _, checks in data.items() for check in checks]
    print("INFO: Skipping checks covered by fontspector.")
except Exception:
    fontspector_checks = []
    print(
        "INFO: fontspector not found or something else happened; running checks covered by fontspector."
    )

# NOTE: Consider the fontspector configuration the source of truth. We want to
# phase out the use of fontbakery.
CHECKS_TO_IGNORE_TOML = Path(__file__).parent / "check-googlesans.toml"
CHECKS_TO_IGNORE = tomllib.loads(CHECKS_TO_IGNORE_TOML.read_text())["exclude_checks"]

# Hack to have this be conditional but without appending later
FONTBAKERY_UP_TO_DATE = (
    ["fontbakery_version"]
    if (Path(__file__).parent.parent / "requirements-fb.txt").exists()
    else []
)

PROFILE = {
    "include_profiles": ["googlefonts"],
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
        ]
    },
    "exclude_checks": [
        *GOOGLEFONTS_PROFILE["sections"]["Outline Checks"],  # Separate.
        *FONTBAKERY_UP_TO_DATE,
        *CHECKS_TO_IGNORE,
        *fontspector_checks,
    ],
    "overrides": {
        "varfont/consistent_axes": [
            {
                "code": "missing-axis",
                "status": "WARN",
                "reason": "It's intended as slnt becomes italics",
            }
        ]
    },
}
