#!/usr/bin/env -S uv run --script

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

# /// script
# dependencies = [
#     "fontspectorapi",
#     "fontTools",
# ]
# ///

from datetime import UTC, datetime, timedelta
from pathlib import Path

from fontspectorapi import (
    FAIL,
    INFO,
    PASS,
    SKIP,
    WARN,
    CheckStatuses,
    Message,
    Plugin,
    check,
    plugin_main,
)
from fontspectorapi.utils import (
    UNICODERANGE_DATA,
    chars_in_range,
    compute_unicoderange_bits,
    unicoderange,
    unicoderange_bit_name,
)
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

# Global Google Sans attributes, in 1000 upM font units. Most values are now in
# check-googlesans.toml. The ones remaining here vary between fonts, and its
# simpler to keep them here then duplicate them for every TTF name.
GS_FONTUNIT_ATTRIBUTES_UPRIGHT = {
    "OS/2.ySubscriptXOffset": 0,
    # Commented out values have been intentionally changed
    # "OS/2.ySubscriptXSize": 650,
    # "OS/2.ySubscriptYOffset": 75,
    "OS/2.ySuperscriptXOffset": 0,
    # "OS/2.ySuperscriptXSize": 650,
    # "OS/2.ySuperscriptYOffset": 350,
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


@check(
    id="opentype/global_fu_attributes",
    title="Check attributes match Google Sans",
    rationale="""Check that global font unit attributes match GS v10.001 (taking 
    upM into consideration).""",
)
def opentype_global_fu_attributes(font_path: Path) -> CheckStatuses:
    ttf = TTFont(font_path)

    attrs = (
        GS_FONTUNIT_ATTRIBUTES_ITALIC
        if "Italic" in font_path.stem
        else GS_FONTUNIT_ATTRIBUTES_UPRIGHT
    )

    # GS is using 1000 upM, GSF is using something else.
    upm_scale = ttf["head"].unitsPerEm / 1000  # type: ignore

    all_match = True
    for attr, expected in attrs.items():
        table_name, attr = attr.split(".", maxsplit=1)
        table = ttf[table_name]
        scaled_expected = expected * upm_scale
        if scaled_expected.is_integer():
            scaled_expected = int(scaled_expected)
        if (actual := getattr(table, attr)) != scaled_expected:
            all_match = False
            yield (
                FAIL,
                f"{table_name}.{attr} should be {scaled_expected} but is {actual}",
            )

    if all_match:
        yield PASS, "All global attributes match."


@check(
    id="googlesans/opentype/os2/unicode_range_bits",
    title="Ensure UnicodeRange bits are properly set",
    rationale="""
        When the UnicodeRange bits on the OS/2 table are not properly set, some programs
        running on Windows may not recognize the font and use a system fallback font
        instead. For that reason, this check calculates the proper settings by inspecting
        the glyphs declared on the cmap table and then ensures that their corresponding
        ranges are enabled.
    """,
)
def unicode_range_bits(
    font_path: Path,
) -> CheckStatuses:
    ttf = TTFont(font_path)
    unicode_range = unicoderange(ttf)
    expected_unicoderange = compute_unicoderange_bits(ttf)
    difference = unicode_range ^ expected_unicoderange
    if not difference:
        yield PASS, "Unicode range bits are properly set"
    else:
        for bit in range(128):
            if difference & (1 << bit):
                range_name = unicoderange_bit_name(bit)
                num_chars = len(chars_in_range(ttf, bit))
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
    id="opentype/head/created",
    title="Check the created date hasn't changed",
    rationale="""
        The `created` date in the OpenType `head` table should be maintained
        across releases.
    """,
)
def head_created(font_path: Path) -> CheckStatuses:
    ttf = TTFont(font_path)

    # Serialised creation date is the number of seconds since this epoch
    # See: https://learn.microsoft.com/en-us/typography/opentype/spec/head
    opentype_epoch = datetime(
        year=1904, month=1, day=1, hour=0, minute=0, second=0, tzinfo=UTC
    )
    actual = opentype_epoch + timedelta(seconds=ttf["head"].created)  # type: ignore

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
    id="vf/fvaraxes",
    title="Ensure all expected axes are present",
    rationale="""
    Confirms that the variable font format builds include
    all expected axis tags
    """,
)
def variable_fvar_axes(font_path: Path) -> CheckStatuses:
    ttf = TTFont(font_path)

    if (fvar := ttf.get("fvar")) is None:
        yield SKIP, "Not a VF"
        return

    font_name = font_path.name
    if SUFFIX_FULL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_FULL_VF.keys()
    elif SUFFIX_PARTIAL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS.keys()
    elif SUFFIX_WORKSPACE_WEIGHT_ONLY_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_WORKSPACE.keys()
    else:
        raise ValueError("Unknown variable font build")
    observed_axis_list = {axis.axisTag for axis in fvar.axes}

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
    id="vf/axis_names",
    title="Check axes names",
    rationale="Confirms that axes have the expected names.",
)
def axis_names(font_path: Path) -> CheckStatuses:
    ttf = TTFont(font_path)
    font_name = font_path.name

    names = ttf["name"]
    if (fvar := ttf.get("fvar")) is None:
        yield SKIP, "Not a VF"
        return

    if SUFFIX_FULL_VF in font_name:
        axis_names = AXIS_NAMES_FULL_VF
    elif SUFFIX_PARTIAL_VF in font_name:
        axis_names = AXIS_NAMES
    elif SUFFIX_WORKSPACE_WEIGHT_ONLY_VF in font_name:
        axis_names = AXIS_NAMES_WORKSPACE
    else:
        raise Exception("Unknown variable font build")

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
    id="vf/fvardefault",
    title="Check axis defaults",
    rationale="""
    Confirms that the variable font format builds include the expected fvar
    default definitions for the Google Sans design axes
    """,
)
def fvar_default(font_path: Path) -> CheckStatuses:
    ttf = TTFont(font_path)

    if (fvar := ttf.get("fvar")) is None:
        yield SKIP, "Not a VF"
        return

    font_name = font_path.name
    if SUFFIX_FULL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_FULL_VF
    elif SUFFIX_PARTIAL_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS
    elif SUFFIX_WORKSPACE_WEIGHT_ONLY_VF in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_WORKSPACE
    else:
        raise Exception("Unknown variable font build")

    for axis in fvar.axes:
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
    title="Check yMin & yMax for Android builds",
    rationale="Confirms the Android-specific Flex build has the correct yMin/yMax",
)
def android_ymin_ymax(font_path: Path) -> CheckStatuses:
    if font_path.parent.name != "android":
        yield SKIP, "Not Android flavour Flex"
        return

    ttf = TTFont(font_path)
    head = ttf["head"]
    if head.yMin != -605:
        yield FAIL, f"yMin was {head.yMin} instead of -605"
    if head.yMax != 2007:
        yield FAIL, f"yMax was {head.yMax} instead of 2007"


# Copy of the check from fontbakery 1.0.1 to ignore our Android font without a
# HVAR table.
@check(
    id="vf/has_HVAR",
    title="Check HVAR is present for non-Android builds",
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
    proposal="https://github.com/fonttools/fontbakery/issues/2119",
)
def has_hvar_table(font_path: Path) -> CheckStatuses:
    ttf = TTFont(font_path)

    match (font_path.parent.name == "android", "HVAR" in ttf):
        case (False, False):
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
        case (False, True):
            yield PASS, "HVAR present"
        case (True, False):
            yield PASS, "Android build shouldn't have HVAR"
        case (True, True):
            yield FAIL, "Android build has HVAR table when it shouldn't"


@check(
    id="googlesansflex/opentype/BASE",
    title="Font has BASE table",
    rationale="Checks that the font has a BASE table",
)
def has_base_table(font_path: Path) -> CheckStatuses:
    ttf = TTFont(font_path)

    if "GoogleSansFlexTV" in font_path.stem:
        yield SKIP, "The TV font does not need a BASE table"
        return
    if font_path.parent == "android":
        yield (
            INFO,
            "The Android font should not have a BASE table until something elsewhere is fixed. See https://github.com/googlefonts/googlesans-flex/issues/1262",
        )
        return

    if "BASE" in ttf:
        yield PASS, "BASE table present in font"
    else:
        yield FAIL, "Missing BASE table"


def register(plugin: Plugin) -> None:
    CHECKS = (
        opentype_global_fu_attributes,
        unicode_range_bits,
        head_created,
        variable_fvar_axes,
        axis_names,
        fvar_default,
        android_ymin_ymax,
        has_hvar_table,
        has_base_table,
    )
    plugin.register_simple_profile(
        "gs-custom", CHECKS, section_name="Google Sans Flex Custom Checks"
    )


if __name__ == "__main__":
    raise SystemExit(plugin_main(register, plugin_name="gs-custom"))
