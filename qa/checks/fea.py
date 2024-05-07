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

from fontbakery.prelude import FAIL, PASS, check, condition
from fontbakery.testable import Font

GOOGLESANS_PROFILE_CHECKS = [
    "com.google.fonts/check/googlesans/features/variableuprights",
    # "com.google.fonts/check/googlesans/features/regression",  # TODO: For later.
]

# v1.100 feature set:
VAR_UPRIGHT_FEA = [
    "aalt",
    "calt",
    "ccmp",
    "dlig",
    "dnom",
    "frac",
    "kern",
    "liga",
    "lnum",
    "locl",
    "mark",
    "mkmk",
    "numr",
    "ordn",
    "pnum",
    "sinf",
    "ss01",
    "ss02",
    "subs",
    "sups",
    "tnum",
    "zero",
]


# ================================================
#
# Conditions
#
# ================================================


@condition(Font)
def is_italic(font: Font):
    return "Italic" in font.ttFont.reader.file.name


@condition(Font)
def is_not_italic(font: Font):
    return "Italic" not in font.ttFont.reader.file.name


@condition(Font)
def is_not_variable_font(font: Font):
    return "fvar" not in font.ttFont.keys()


@condition(Font)
def is_variable_font(font: Font):
    return "fvar" in font.ttFont.keys()


# ================================================
# Feature support
# ================================================


@check(
    id="com.google.fonts/check/googlesans/features/variableuprights",
    conditions=["is_not_italic", "is_variable_font"],
    rationale="""
    Confirms that the variable upright builds contain expected feature tags.
    """,
)
def com_google_fonts_check_googlesans_features_variable_uprights(ttFont):
    """Confirms that the upright builds contain expected feature tags."""
    tt = ttFont
    gpos = tt.get("GPOS")
    gsub = tt.get("GSUB")

    if gpos is None or gsub is None:
        yield FAIL, "Font must contain a 'GPOS' and 'GSUB' table"
        return

    fea_tags = set()

    for gpos_record in gpos.table.FeatureList.FeatureRecord:
        fea_tags.add(gpos_record.FeatureTag)

    for gsub_record in gsub.table.FeatureList.FeatureRecord:
        fea_tags.add(gsub_record.FeatureTag)

    if sorted(fea_tags) == VAR_UPRIGHT_FEA:
        yield PASS, "Font contains the expected feature tags"
    else:
        yield (
            FAIL,
            "Font does not contain the expected feature tags.\n"
            f"Found:{sorted(fea_tags)}\nExpected:{VAR_UPRIGHT_FEA}",
        )
