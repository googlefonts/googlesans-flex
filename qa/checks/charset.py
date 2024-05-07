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

import os
from difflib import unified_diff
from pathlib import Path

from fontbakery.prelude import check, FAIL, PASS

# ================================================
# Glyph set checks
# ================================================

# ::::::::::::::::::::::::::::::::::::::::::::::::
# Glyph set support
# ::::::::::::::::::::::::::::::::::::::::::::::::
# compare against a newline-delimited list of expected glyph names
# this includes all Unicode encoded and non-Unicode encoded glyph definitions


@check(
    id="com.google.fonts/check/googlesans/glyphs/glyphset-contents",
    rationale="""
    Confirms that the fonts include all expected Unicode encoded and \
    non-Unicode encoded glyph definitions. This test also confirms that \
    fonts have the expected glyph order.
    """,
)
def com_google_fonts_check_googlesans_glyphs_glyphset_contents(font, ttFont):
    """Confirm that fonts have all expected Unicode encoded and non-Unicoded
    encoded glyph definitions.This test also confirms that the glyph order
    is defined as expected."""

    glyph_definition_basedir = os.path.join("qa", "definitions")

    tests_passed = True
    glyph_list_raw = ""
    base_file_path = os.path.basename(font.file) + ".glyphsetdef"
    expected_glyph_definition_path = os.path.join(
        glyph_definition_basedir, base_file_path
    )
    with open(expected_glyph_definition_path, "r") as f:
        glyph_list_raw = f.read().rstrip()

    glyph_list = glyph_list_raw.split("\n")
    # must have
    # (1) glyph set contents &
    # (2) glyph set order as defined in def file
    if not (ttFont.getGlyphOrder() == glyph_list):
        tests_passed = False
        yield (
            FAIL,
            ("Font failed expected glyph set check. Diffs:\n\n```diff\n{}\n```").format(
                "\n".join(
                    unified_diff(
                        list(ttFont.getGlyphOrder()),
                        list(glyph_list),
                        fromfile="ttFont.getGlyphOrder()",
                        tofile="glyphsetdef",
                        lineterm="",
                    )
                ),
            ),
        )
    if tests_passed:
        yield PASS, "All fonts passed the expected glyph set checks"
