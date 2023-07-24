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
from fontbakery.callable import check, condition
from fontbakery.checkrunner import FAIL, PASS, SKIP, WARN, Section
from fontbakery.constants import UNICODERANGE_DATA
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.profiles.outline import OUTLINE_PROFILE_CHECKS
from fontbakery.profiles.shared_conditions import is_italic
from fontbakery.utils import (
    chars_in_range,
    compute_unicoderange_bits,
    unicoderange_bit_name,
)

profile_imports = ("fontbakery.profiles.googlefonts",)
profile = profile_factory(default_section=Section("Google Sans Flex Custom Checks"))

GOOGLESANSFLEX_PROFILE_CHECKS = GOOGLEFONTS_PROFILE_CHECKS + [
    "com.google.fonts/check/googlesansflex/opentype/os2/unicode_range_bits",
    "com.google.fonts/check/googlesansflex/vf/fvaraxes",
    "com.google.fonts/check/googlesansflex/vf/axis_names",
    "com.google.fonts/check/googlesansflex/vf/fvardefault",
    "com.google.fonts/check/googlesansflex/opentype/global_fu_attributes",
    "com.google.fonts/check/googlesansflex/round_reflow",
]

# define check ID's in the upstream `googlefonts` profile
# that should be excluded here
excluded_check_ids = (
    *OUTLINE_PROFILE_CHECKS,  # Separate.
    "com.google.fonts/check/ftxvalidator_is_available",
    "com.google.fonts/check/dsig",
    "com.google.fonts/check/unwanted_tables",
    "com.google.fonts/check/contour_count",  # design rather than QA problem
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids",  # Bogus
    "com.google.fonts/check/varfont/regular_wght_coord",  # Buggy in 0.8.9
    "com.google.fonts/check/varfont/bold_wght_coord",  # Buggy in 0.8.9
    "com.google.fonts/check/vertical_metrics",  # GS is our reference.
    "com.google.fonts/check/varfont/regular_opsz_coord",  # No, opsz=18
    "com.google.fonts/check/glyph_coverage",  # We have our own target
    "com.google.fonts/check/file_size",  # We're going bigger
    "com.google.fonts/check/font_names",  # We have our own naming ideas
)

AXIS_DEFAULTS = {
    "opsz": 18,
    "wdth": 100,
    "wght": 400,
    "ROND": 0,
}

AXIS_NAMES = {
    "opsz": "Optical Size",
    "ROND": "Roundness",
    "wdth": "Width",
    "wght": "Weight",
}

AXIS_DEFAULTS_FULL_VF = {
    **AXIS_DEFAULTS,
    "slnt": 0,
}

AXIS_NAMES_FULL_VF = {
    **AXIS_NAMES,
    "slnt": "Slant",
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
    "OS/2.ySubscriptXSize": 650,
    "OS/2.ySubscriptYOffset": 75,
    "OS/2.ySubscriptYSize": 600,
    "OS/2.ySuperscriptXOffset": 0,
    "OS/2.ySuperscriptXSize": 650,
    "OS/2.ySuperscriptYOffset": 350,
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
def com_google_fonts_check_googlesansflex_opentype_global_fu_attributes(ttFont):
    """Check that global font unit attributes match GS v10.001 (taking upM into
    consideration)."""

    if is_italic(ttFont):
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
            yield FAIL, f"{table_name}.{attr} should be {scaled_expected} but is {actual}"

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
                    yield FAIL, Message(
                        "bad-range-bit",
                        f"UnicodeRange bit {bit} '{range_name}' should be {set_unset} "
                        f"because cmap has {num_chars} of the {range_size} codepoints "
                        f"in this range.",
                    )
                else:
                    set_unset = "1"
                    yield WARN, Message(
                        "bad-range-bit",
                        f"UnicodeRange bit {bit} '{range_name}' should be {set_unset} "
                        f"because cmap has {num_chars} of the {range_size} codepoints "
                        f"in this range.",
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
    font_name = Path(font).name
    if "[ROND,opsz,slnt,wdth,wght]" in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_FULL_VF.keys()
    elif "[ROND,opsz,wdth,wght]" in font_name:
        expected_fvar_axes = AXIS_DEFAULTS.keys()
    else:
        raise Exception("Unknown variable font build")
    observed_axis_list = {axis.axisTag for axis in ttFont["fvar"].axes}

    if observed_axis_list != expected_fvar_axes:
        yield FAIL, (
            f"Font does not include the correct axis tags. \n"
            f"Observed: {observed_axis_list}\n"
            f"Expected: {expected_fvar_axes}"
        )
    else:
        yield PASS, "Font includes all expected axis tags"


@check(
    id="com.google.fonts/check/googlesansflex/vf/axis_names",
    conditions=["is_variable_font"],
)
def com_google_fonts_check_googlesansflex_axis_names(font, ttFont):
    """Confirms that axes have the expected names."""
    font_name = Path(font).name
    if "[ROND,opsz,slnt,wdth,wght]" in font_name:
        axis_names = AXIS_NAMES_FULL_VF
    elif "[ROND,opsz,wdth,wght]" in font_name:
        axis_names = AXIS_NAMES
    else:
        raise Exception("Unknown variable font build")

    names = ttFont["name"]
    fvar = ttFont["fvar"]

    for axis in fvar.axes:
        name = names.getDebugName(axis.axisNameID)
        expected = axis_names.get(axis.axisTag)
        if expected is None:
            yield WARN, f"Font has unexpected axis tagged {axis.axisTag}"
        elif name == expected:
            yield PASS, f"Axis tagged {axis.axisTag} has expected name {expected}"
        else:
            yield WARN, f"Axis tagged {axis.axisTag} has name {name} but should be named {expected}"


@check(
    id="com.google.fonts/check/googlesansflex/vf/fvardefault",
    conditions=["is_variable_font"],
    rationale="""
    Confirms that the variable font format builds include the expected fvar
    default definitions for the Google Sans design axes
    """,
)
def com_google_fonts_check_googlesansflex_variable_fvar_default(font, ttFont):
    """Confirms that the variable font builds include correct fvar default."""
    font_name = Path(font).name
    if "[ROND,opsz,slnt,wdth,wght]" in font_name:
        expected_fvar_axes = AXIS_DEFAULTS_FULL_VF
    elif "[ROND,opsz,wdth,wght]" in font_name:
        expected_fvar_axes = AXIS_DEFAULTS
    else:
        raise Exception("Unknown variable font build")

    for axis in ttFont["fvar"].axes:
        tag = axis.axisTag
        expected = expected_fvar_axes.get(tag)
        if expected is None:
            yield FAIL, f"Font has unexpected axis tagged {tag}"
        elif axis.defaultValue != expected:
            yield FAIL, (
                f"Font does not include the correct "
                f"fvar {tag} axis default.\n"
                f"Found: `{axis.defaultValue}` and expected `{expected}`"
            )
        else:
            yield PASS, f"Font contains the expected fvar {tag} default."


@condition
def rond_axis(ttFont):
    if "fvar" in ttFont:
        for axis in ttFont["fvar"].axes:
            if axis.axisTag == "ROND":
                return axis


@check(
    id="com.google.fonts/check/googlesansflex/round_reflow",
    rationale="""
        The round (ROND) axis should not change any advanceWidth or kerning data
        across its design space. This is because altering the advance width of glyphs
        can cause text reflow.
    """,
    conditions=["is_variable_font"],
    proposal="https://github.com/googlefonts/fontbakery/issues/3187",
)
def com_google_fonts_check_googlesansflex_round_reflow(ttFont, config):
    """Ensure VFs with the GRAD axis do not vary horizontal advance."""
    from fontbakery.utils import all_kerning, pretty_print_list

    if not rond_axis(ttFont):
        yield SKIP, Message("no-rond", "This font has no ROND axis")
        return

    gvar = ttFont["gvar"]
    bad_glyphs = set()
    for glyph, deltas in gvar.variations.items():
        for delta in deltas:
            if "ROND" not in delta.axes:
                continue
            if any(c is not None and c != (0, 0) for c in delta.coordinates[-4:]):
                bad_glyphs.add(glyph)

    if bad_glyphs:
        bad_glyphs_list = pretty_print_list(config, list(bad_glyphs))
        yield FAIL, Message(
            "rond-causes-reflow",
            f"The following glyphs have variation in horizontal"
            f" advance due to the ROND axis: {bad_glyphs_list}",
        )

    # Determine if any kerning rules vary the horizontal advance.
    # This is going to get grubby.
    bad_kerning = False

    if "GDEF" in ttFont and hasattr(ttFont["GDEF"].table, "VarStore"):
        effective_regions = []
        varstore = ttFont["GDEF"].table.VarStore
        regions = varstore.VarRegionList.Region
        rond_index = [x.axisTag == "ROND" for x in ttFont["fvar"].axes].index(True)
        for ix, region in enumerate(regions):
            axis_tent = region.VarRegionAxis[rond_index]
            effective = (
                axis_tent.StartCoord != axis_tent.PeakCoord
                or axis_tent.PeakCoord != axis_tent.EndCoord
            )
            if effective:
                effective_regions.append(ix)

        # Some regions vary *something* along the ROND axis. But what?
        if effective_regions:
            kerning = all_kerning(ttFont)
            for left, right, v1, _ in kerning:
                if v1 and hasattr(v1, "XAdvDevice") and v1.XAdvDevice:
                    variation = [v1.XAdvDevice.StartSize, v1.XAdvDevice.EndSize]
                    regions = varstore.VarData[variation[0]].VarRegionIndex
                    if any(region in effective_regions for region in regions):
                        deltas = varstore.VarData[variation[0]].Item[variation[1]]
                        effective_deltas = [
                            deltas[ix]
                            for ix, region in enumerate(regions)
                            if region in effective_regions
                        ]
                        if any(x for x in effective_deltas):
                            yield FAIL, Message(
                                "rond-kern-causes-reflow",
                                f"Kerning rules cause variation in"
                                f" horizontal advance on the ROND axis"
                                f" (e.g. {left}/{right})",
                            )
                            bad_kerning = True
                            break

    # Check kerning here
    if not bad_glyphs and not bad_kerning:
        yield PASS, (
            "No variations or kern rules vary horizontal advance along the ROND axis"
        )


# ================================================
#
# End check definitions
#
# ================================================


# skip filter function to exclude checks defined in the
# fontbakery universal profile
def check_skip_filter(checkid, font=None, **iterargs):
    if font and checkid in excluded_check_ids:
        return False, ("Check skipped in Google Sans Flex profile")
    return True, None


profile.check_skip_filter = check_skip_filter
profile.auto_register(globals())
profile.test_expected_checks(GOOGLESANSFLEX_PROFILE_CHECKS, exclusive=True)
