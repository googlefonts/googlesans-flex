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


from datetime import UTC, datetime, timedelta
from pathlib import Path

from fontTools.ttLib import TTFont
from fontbakery.callable import check
from fontbakery.constants import UNICODERANGE_DATA
from fontbakery.message import Message
from fontbakery.status import FAIL, PASS, SKIP, WARN
from fontbakery.testable import Font
from fontbakery.utils import (
    chars_in_range,
    compute_unicoderange_bits,
    unicoderange_bit_name,
)

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

# Taken from 2.003 release TTF
GS_CREATION_DATE = datetime(
    year=2017, month=7, day=6, hour=9, minute=41, second=44, tzinfo=UTC
)

# ================================================
#
# Begin check definitions
#
# ================================================


# ================================================
# OpenType table attribute checks
# ================================================


@check(id="googlesansflex/opentype/global_fu_attributes")
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
    id="googlesansflex/opentype/os2/unicode_range_bits",
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


@check(
    id="googlesansflex/opentype/head/created",
    rationale="""
        The `created` date in the OpenType `head` table should be maintained
        across releases.
    """,
)
def com_google_fonts_check_googlesansflex_head_created(ttFont):
    """
    The `created` date in the OpenType `head` table should be maintained across
    releases.
    """

    # Serialised creation date is the number of seconds since this epoch
    # See: https://learn.microsoft.com/en-us/typography/opentype/spec/head
    opentype_epoch = datetime(
        year=1904, month=1, day=1, hour=0, minute=0, second=0, tzinfo=UTC
    )
    actual = opentype_epoch + timedelta(seconds=ttFont["head"].created)

    if actual == GS_CREATION_DATE:
        yield PASS, "Creation date in `head` is unchanged since initial release."
    else:
        yield (
            FAIL,
            f"Creation date in `head` has been modified since initial release: expected '{GS_CREATION_DATE}' but saw '{actual}'.",
        )


# ================================================
# Variable build format specific
# ================================================


@check(
    id="googlesansflex/vf/fvaraxes",
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
    id="googlesansflex/vf/axis_names",
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
    id="googlesansflex/vf/fvardefault",
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
    id="googlesansflex/android_ymin_ymax",
    rationale="""
    Confirms the Android-specific Flex build has the correct yMin/yMax
    """,
)
def com_google_fonts_check_android_ymin_ymax(font: Font, ttFont: TTFont):
    """Confirms the Android-specific Flex build has the correct yMin/yMax"""
    font_path = Path(font.file)
    if font_path.parent.name != "android":
        yield SKIP, "Not Android flavour Flex"
        return

    # Reopen the font fresh because the ttFont we get as argument seems to have
    # had its head yMin and yMax recomputed to the values from the font,
    # instead of the hardcoded ones for Android.

    ttFont2 = TTFont(font_path)

    head = ttFont2["head"]
    if head.yMin != -605:
        yield FAIL, f"yMin was {head.yMin} instead of -605"
    if head.yMax != 2007:
        yield FAIL, f"yMax was {head.yMax} instead of 2007"


# Copy of the check from fontbakery 1.0.1 to ignore our Android font without a
# HVAR table.
@check(
    id="googlesansflex/varfont/has_HVAR",
    rationale="""
        Not having a HVAR table can lead to costly text-layout operations on some
        platforms, which we want to avoid.

        So, all variable fonts on the Google Fonts collection should have an HVAR
        with valid values.

        More info on the HVAR table can be found at:
        https://docs.microsoft.com/en-us/typography/opentype/spec/otvaroverview#variation-data-tables-and-miscellaneous-requirements
    """,
    # FIX-ME: We should clarify which are these platforms in which there can be issues
    #         with costly text-layout operations when an HVAR table is missing!
    conditions=["is_variable_font"],
    proposal="https://github.com/fonttools/fontbakery/issues/2119",
)
def check_varfont_has_HVAR(ttFont):
    """Check that variable fonts have an HVAR table."""

    font_path = Path(ttFont.reader.file.name)
    if font_path.parent.name == "android":
        yield SKIP, "Android flavour Flex has no HVAR"
        return

    if "HVAR" not in ttFont.keys():
        yield (
            FAIL,
            Message(
                "lacks-HVAR",
                "All variable fonts on the Google Fonts collection"
                " must have a properly set HVAR table in order"
                " to avoid costly text-layout operations on"
                " certain platforms.",
            ),
        )


@check(
    id="googlesansflex/android_hvar",
    rationale="""
    Confirms the Android-specific Flex build has no `HVAR` table.

    See: https://github.com/googlefonts/googlesans-flex/issues/1154
    """,
)
def com_google_fonts_check_android_hvar(font: Font, ttFont: TTFont):
    """Confirms the Android-specific Flex build has no `HVAR` table"""

    font_path = Path(font.file)
    if font_path.parent.name != "android":
        yield SKIP, "Not Android flavour Flex"
        return

    if "HVAR" in ttFont:
        yield FAIL, f"{font_path} contains an `HVAR` table, but should not"
