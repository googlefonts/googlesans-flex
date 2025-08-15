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

from fontbakery.profiles.googlefonts import PROFILE as GOOGLEFONTS_PROFILE


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
        "dsig",
        "unwanted_tables",
        "contour_count",  # design rather than QA problem
        "opentype/varfont/valid_default_instance_nameids",  # Bogus
        "family/vertical_metrics",  # GS is our reference.
        "opentype/varfont/regular_opsz_coord",  # No, opsz=18
        "googlefonts/glyph_coverage",  # We have our own target
        "file_size",  # We're going bigger
        "googlefonts/font_names",  # We have our own naming ideas
        "opentype/family/bold_italic_unique_for_nameid1",  # Expected and desired
        "googlefonts/STAT/axisregistry",  # https://github.com/fonttools/fontbakery/discussions/4214
        "fontdata_namecheck",  # online resource unavailable https://github.com/fonttools/fontbakery/issues/2719
        "STAT_strings",  # we're intentionally calling slant italic https://github.com/googlefonts/googlesans-flex/issues/774#issuecomment-1921326716
        "googlefonts/STAT",  # https://github.com/googlefonts/googlesans-flex/issues/835#issuecomment-1930057206
        "googlefonts/glyphsets/shape_languages",  # we do our own shaperglot check
        "family/single_directory",  # conflicts with gftools' folder structure
        "opentype/family/consistent_family_name",  # intended with our statics
        "name/family_and_style_max_length",  # we know our statics exceed this limit and it's okay
        "opentype/varfont/family_axis_ranges",  # our workspace fonts intentionally change axes ranges
        "googlefonts/varfont/has_HVAR",  # The Android font has no HVAR, so we had to modify this check into `googlesansflex/varfont/has_HVAR`
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
