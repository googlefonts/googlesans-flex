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

from fontbakery.callable import check
from fontbakery.constants import UNICODERANGE_DATA
from fontbakery.message import Message
from fontbakery.status import FAIL, PASS, WARN
from fontbakery.testable import Font
from fontbakery.utils import (
    chars_in_range,
    compute_unicoderange_bits,
    unicoderange_bit_name,
)
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

# Each VF we build will have one of these suffixes depending on whether it
# includes the full designspace or is restricted to upright or italic only.
SUFFIX_FULL_VF = "[GRAD,ROND,opsz,slnt,wdth,wght]"
SUFFIX_PARTIAL_VF = "[GRAD,ROND,opsz,wdth,wght]"
SUFFIX_WORKSPACE_WEIGHT_ONLY_VF = "[wght]"

AXIS_DEFAULTS = {
    "opsz": 18,
    "wdth": 100,
    "wght": 400,
    "ROND": 0,
    "GRAD": 0,
}

AXIS_NAMES = {
    "opsz": "Optical Size",
    "ROND": "Roundness",
    "wdth": "Width",
    "wght": "Weight",
    "GRAD": "Grade",
}

AXIS_DEFAULTS_FULL_VF = {
    **AXIS_DEFAULTS,
    "slnt": 0,
}

AXIS_NAMES_FULL_VF = {
    **AXIS_NAMES,
    "slnt": "Slant",
}

AXIS_DEFAULTS_WORKSPACE = {
    "wght": 400,
}

AXIS_NAMES_WORKSPACE = {
    "wght": "Weight",
}

# Global Google Sans attributes, in 1000 upM font units.
GS_FONTUNIT_ATTRIBUTES_UPRIGHT = {
    "hhea.ascender": 966,
    "hhea.descender": -286,
    "hhea.lineGap": 0,
    "OS/2.sTypoAscender": 966,  # set to match hhea metrics values
    "OS/2.sTypoDescender": -286,
    "OS/2.sTypoLineGap": 0,
    "OS/2.yStrikeoutPosition": 306,
    "OS/2.yStrikeoutSize": 84,
    "OS/2.ySubscriptXOffset": 0,
    # Commented out values have been intentionally changed
    # "OS/2.ySubscriptXSize": 650,
    # "OS/2.ySubscriptYOffset": 75,
    "OS/2.ySubscriptYSize": 600,
    "OS/2.ySuperscriptXOffset": 0,
    # "OS/2.ySuperscriptXSize": 650,
    # "OS/2.ySuperscriptYOffset": 350,
    "OS/2.ySuperscriptYSize": 600,
    "post.underlinePosition": -160,
    "post.underlineThickness": 84,
}

GS_FONTUNIT_ATTRIBUTES_ITALIC = {
    **GS_FONTUNIT_ATTRIBUTES_UPRIGHT,
    "OS/2.ySubscriptXOffset": -13,
    "OS/2.ySuperscriptXOffset": 62,
}

# ================================================
#
# Begin check definitions
#
# ================================================


# ================================================
# OpenType table attribute checks
# ================================================


@check(id="com.google.fonts/check/googlesansflex/opentype/global_fu_attributes")
def com_google_fonts_check_googlesansflex_opentype_global_fu_attributes(
    font: Font, ttFont
):
    """Check that global font unit attributes match GS v10.001 (taking upM into
    consideration)."""

    if font.is_italic:
        attrs = GS_FONTUNIT_ATTRIBUTES_ITALIC
    else:
        attrs = GS_FONTUNIT_ATTRIBUTES_UPRIGHT

    # GS is using 1000 upM, GSF may use something else.
    upm_scale = ttFont["head"].unitsPerEm / 1000

    matches = True
    for attr, expected in attrs.items():
        table_name, attr = attr.split(".")
        table = ttFont[table_name]
        scaled_expected = expected * upm_scale
        if scaled_expected.is_integer():
            scaled_expected = int(scaled_expected)
        if (actual := getattr(table, attr)) != scaled_expected:
            matches = False
            yield (
                FAIL,
                f"{table_name}.{attr} should be {scaled_expected} but is {actual}",
            )

    if matches:
        yield PASS, "All global attributes match."


@check(
    id="com.google.fonts/check/googlesansflex/opentype/os2/unicode_range_bits",
    rationale="""
        When the UnicodeRange bits on the OS/2 table are not properly set, some programs
        running on Windows may not recognize the font and use a system fallback font
        instead. For that reason, this check calculates the proper settings by inspecting
        the glyphs declared on the cmap table and then ensures that their corresponding
        ranges are enabled.
    """,
    conditions=["unicoderange"],
)
def com_google_fonts_check_googlesansflex_unicode_range_bits(ttFont, unicoderange):
    """Ensure UnicodeRange bits are properly set."""
    expected_unicoderange = compute_unicoderange_bits(ttFont)
    difference = unicoderange ^ expected_unicoderange
    if not difference:
        yield PASS, "Unicode range bits are properly set"
    else:
        for bit in range(128):
            if difference & (1 << bit):
                range_name = unicoderange_bit_name(bit)
                num_chars = len(chars_in_range(ttFont, bit))
                range_size = sum(
                    entry[3] - entry[2] + 1 for entry in UNICODERANGE_DATA[bit]
                )
                if num_chars == 0:
                    set_unset = "0"
                    num_chars = "none"
                    yield (
                        FAIL,
                        Message(
                            "bad-range-bit",
                            f"UnicodeRange bit {bit} '{range_name}' should be {set_unset} "
                            f"because cmap has {num_chars} of the {range_size} codepoints "
                            f"in this range.",
                        ),
                    )
                else:
                    set_unset = "1"
                    yield (
                        WARN,
                        Message(
                            "bad-range-bit",
                            f"UnicodeRange bit {bit} '{range_name}' should be {set_unset} "
                            f"because cmap has {num_chars} of the {range_size} codepoints "
                            f"in this range.",
                        ),
                    )


# ================================================
# Variable build format specific
# ================================================


@check(
    id="com.google.fonts/check/googlesansflex/vf/fvaraxes",
    conditions=["is_variable_font"],
    rationale="""
    Confirms that the variable font format builds include
    all expected axis tags
    """,
)
def com_google_fonts_check_googlesansflex_variable_fvar_axes(font, ttFont):
    """Confirms that the variable font builds include expected axes."""
    font_name = Path(font.file).name
    if SUFFIX_FULL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_FULL_VF.keys()
    elif SUFFIX_PARTIAL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS.keys()
    elif SUFFIX_WORKSPACE_WEIGHT_ONLY_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_WORKSPACE.keys()
    else:
        raise Exception("Unknown variable font build")
    observed_axis_list = {axis.axisTag for axis in ttFont["fvar"].axes}

    if observed_axis_list != expected_fvar_axes:
        yield (
            FAIL,
            (
                f"Font does not include the correct axis tags. \n"
                f"Observed: {observed_axis_list}\n"
                f"Expected: {expected_fvar_axes}"
            ),
        )
    else:
        yield PASS, "Font includes all expected axis tags"


@check(
    id="com.google.fonts/check/googlesansflex/vf/axis_names",
    conditions=["is_variable_font"],
)
def com_google_fonts_check_googlesansflex_axis_names(font: Font, ttFont):
    """Confirms that axes have the expected names."""
    font_name = Path(font.file).name
    if SUFFIX_FULL_VF in font_name:
        axis_names = AXIS_NAMES_FULL_VF
    elif SUFFIX_PARTIAL_VF in font_name:
        axis_names = AXIS_NAMES
    elif SUFFIX_WORKSPACE_WEIGHT_ONLY_VF in font_name:
        axis_names = AXIS_NAMES_WORKSPACE
    else:
        raise Exception("Unknown variable font build")

    names = ttFont["name"]
    fvar = ttFont["fvar"]

    for axis in fvar.axes:
        name = names.getDebugName(axis.axisNameID)
        expected = axis_names.get(axis.axisTag)
        if expected is None:
            yield FAIL, f"Font has unexpected axis tagged {axis.axisTag}"
        elif name == expected:
            yield PASS, f"Axis tagged {axis.axisTag} has expected name {expected}"
        else:
            yield (
                FAIL,
                f"Axis tagged {axis.axisTag} has name {name} but should be named {expected}",
            )


@check(
    id="com.google.fonts/check/googlesansflex/vf/fvardefault",
    conditions=["is_variable_font"],
    rationale="""
    Confirms that the variable font format builds include the expected fvar
    default definitions for the Google Sans design axes
    """,
)
def com_google_fonts_check_googlesansflex_variable_fvar_default(font: Font, ttFont):
    """Confirms that the variable font builds include correct fvar default."""
    font_name = Path(font.file).name
    if SUFFIX_FULL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_FULL_VF
    elif SUFFIX_PARTIAL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS
    elif SUFFIX_WORKSPACE_WEIGHT_ONLY_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_WORKSPACE
    else:
        raise Exception("Unknown variable font build")

    for axis in ttFont["fvar"].axes:
        tag = axis.axisTag
        expected = expected_fvar_axes.get(tag)
        if expected is None:
            yield FAIL, f"Font has unexpected axis tagged {tag}"
        elif axis.defaultValue != expected:
            yield (
                FAIL,
                (
                    f"Font does not include the correct "
                    f"fvar {tag} axis default.\n"
                    f"Found: `{axis.defaultValue}` and expected `{expected}`"
                ),
            )
        else:
            yield PASS, f"Font contains the expected fvar {tag} default."


@check(
    id="com.google.fonts/check/googlesansflex/vf/win_extremes",
    conditions=["is_variable_font"],
    rationale="""
    Checks that the OS/2.usWinAscent and OS/2.usWinDescent values do not vary
    across the designspace, and that they are sufficient to cover the extremes
    on the y-axis across every glyph at every named instance.

    The former is an engineering decision for Google Sans Flex, in order to have
    consistent Win vertical metrics at every position within the VF and in any
    instanced sub-VFs.

    The latter ensures that clipping does not occur at common non-default
    positions in the designspace. Checking only against yMin and yMax is not
    sufficient to ensure this, as yMin and yMax are defined only for the default
    instance, while extreme vertical coordinates are more likely to occur at
    axis extremes.
    """,
)
def com_google_fonts_check_googlesansflex_vf_win_extremes(ttFont: TTFont):
    """
    Checks that the OS/2.usWinAscent and OS/2.usWinDescent values do not vary
    across the designspace, and that they are sufficient to cover the extremes
    on the y-axis across every glyph at every named instance.
    """

    # Get the OS/2.usWin{Ascent,Descent} metrics.
    ascent: int = ttFont["OS/2"].usWinAscent  # type: ignore
    descent: int = ttFont["OS/2"].usWinDescent  # type: ignore

    # Assert that they do not vary across the designspace.
    mvar = ttFont.get("MVAR")
    if mvar is not None:
        variated_tags = {
            tag for record in mvar.table.ValueRecord for tag in record.ValueTag
        }

        if "hcla" in variated_tags:
            yield FAIL, "TTF varies OS/2.usWinAscent across its designspace"
        if "hcld" in variated_tags:
            yield FAIL, "TTF varies OS/2.usWinDescent across its designspace"

    # TODO: This is only named instances; we should include everywhere we have
    # sources.
    interesting_locations = [
        named_instance.coordinates for named_instance in ttFont["fvar"].instances
    ]

    # Assert that the yMin/yMax of every glyph at every position does not exceed
    # the metrics.
    smallest_y_min = None
    largest_y_max = None
    for location in interesting_locations:
        glyph_set = ttFont.getGlyphSet(
            preferCFF=False, location=location, normalized=False
        )
        for glyph_name in ttFont.getGlyphOrder():
            glyph = glyph_set[glyph_name]
            bounds_pen = BoundsPen(glyph_set)
            glyph.draw(bounds_pen)

            bounds = bounds_pen.bounds
            if bounds is None:
                # Glyph was empty.
                continue

            (_, y_min, _, y_max) = bounds_pen.bounds

            smallest_y_min = (
                y_min if smallest_y_min is None else min(y_min, smallest_y_min)
            )
            largest_y_max = (
                y_max if largest_y_max is None else max(y_max, largest_y_max)
            )

    # TODO: Round floats in some direction (but consider how this will interact with the +1).
    if smallest_y_min is not None and -smallest_y_min >= descent:
        yield FAIL, f"OS/2.usWinDescent must be at least {-smallest_y_min + 1} to extend further than the smallest y coordinate seen in outlines, but was only {descent}"

    if largest_y_max is not None and largest_y_max >= ascent:
        yield FAIL, f"OS/2.usWinAscent must be at least {largest_y_max + 1} to extend further than the largest y coordinate seen in outlines, but was only {ascent}"
