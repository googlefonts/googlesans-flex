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
    id="googlesans/glyphs/glyphset-contents",
    rationale="""
    Confirms that the fonts include all expected Unicode encoded and non-Unicode
    encoded glyph definitions. This test does not require the glyph order to
    match.
    """,
)
def com_google_fonts_check_googlesans_glyphs_glyphset_contents(font, ttFont):
    """
    Confirms that the fonts include all expected Unicode encoded and
    non-Unicode encoded glyph definitions. This test does not require the
    glyph order to match.
    """

    glyph_defs_dir = Path("qa", "definitions")

    glyph_def_name = Path(font.file).name + ".glyphsetdef"
    glyph_def_path = glyph_defs_dir / glyph_def_name

    # Sort to compare without considering order.
    expected_glyphs = sorted(glyph_def_path.read_text().strip().splitlines())
    actual_glyphs = sorted(ttFont.getGlyphOrder())

    if expected_glyphs == actual_glyphs:
        yield PASS, "Font glyphset matches its expected glyphset"
    else:
        yield (
            FAIL,
            (
                "Font glyphset does not match its expected glyphset. Diffs:\n\n```diff\n{}\n```"
            ).format(
                "\n".join(
                    unified_diff(
                        expected_glyphs,
                        actual_glyphs,
                        fromfile="glyphsetdef",
                        tofile="ttFont.getGlyphOrder()",
                        lineterm="",
                    )
                ),
            ),
        )
