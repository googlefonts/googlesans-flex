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

from fontbakery.profiles.outline import PROFILE as OUTLINE_PROFILE


# Hack to have this be conditional but without appending later
FONTBAKERY_UP_TO_DATE = (
    ["com.google.fonts/check/fontbakery_version"]
    if (Path(__file__).parent.parent / "requirements-fb.txt").exists()
    else []
)

PROFILE = {
    "include_profiles": ["googlefonts"],
    "check_definitions": [Path(__file__).parent / "checks" / "googlesans.py"],
    "sections": {
        "Google Sans Flex Custom Checks": [
            "com.google.fonts/check/googlesansflex/opentype/os2/unicode_range_bits",
            "com.google.fonts/check/googlesansflex/vf/fvaraxes",
            "com.google.fonts/check/googlesansflex/vf/axis_names",
            "com.google.fonts/check/googlesansflex/vf/fvardefault",
            "com.google.fonts/check/googlesansflex/opentype/global_fu_attributes",
        ]
    },
    "exclude_checks": [
        *OUTLINE_PROFILE["sections"]["Outline Checks"],  # Separate.
        *FONTBAKERY_UP_TO_DATE,
        "com.google.fonts/check/ftxvalidator_is_available",
        "com.google.fonts/check/dsig",
        "com.google.fonts/check/unwanted_tables",
        "com.google.fonts/check/contour_count",  # design rather than QA problem
        "com.adobe.fonts/check/varfont/valid_default_instance_nameids",  # Bogus
        "com.google.fonts/check/vertical_metrics",  # GS is our reference.
        "com.google.fonts/check/varfont/regular_opsz_coord",  # No, opsz=18
        "com.google.fonts/check/glyph_coverage",  # We have our own target
        "com.google.fonts/check/file_size",  # We're going bigger
        "com.google.fonts/check/font_names",  # We have our own naming ideas
        "com.adobe.fonts/check/family/bold_italic_unique_for_nameid1",  # Expected and desired
        "com.google.fonts/check/STAT/gf_axisregistry",  # https://github.com/fonttools/fontbakery/discussions/4214
        "com.google.fonts/check/fontdata_namecheck",  # online resource unavailable https://github.com/fonttools/fontbakery/issues/2719
        "com.google.fonts/check/STAT_strings",  # we're intentionally calling slant italic https://github.com/googlefonts/googlesans-flex/issues/774#issuecomment-1921326716
        "com.google.fonts/check/STAT",  # https://github.com/googlefonts/googlesans-flex/issues/835#issuecomment-1930057206
        "com.google.fonts/check/glyphsets/shape_languages",  # we do our own shaperglot check
        "com.google.fonts/check/family/single_directory",  # conflicts with gftools' folder structure
        "com.adobe.fonts/check/family/consistent_family_name",  # intended with our statics
        "com.google.fonts/check/name/family_and_style_max_length",  # we know our statics exceed this limit and it's okay
    ],
    "overrides": {
        "com.google.fonts/check/varfont/consistent_axes": [
            {
                "code": "missing-axis",
                "status": "WARN",
                "reason": "It's intended as slnt becomes italics",
            }
        ]
    },
}
