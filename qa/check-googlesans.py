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


from fontbakery.callable import check
from fontbakery.checkrunner import FAIL, PASS, WARN, Section
from fontbakery.constants import UNICODERANGE_DATA
from fontbakery.fonts_profile import profile_factory
from fontbakery.message import Message
from fontbakery.profiles.universal import UNIVERSAL_PROFILE_CHECKS
from fontbakery.profiles.googlefonts import GOOGLEFONTS_PROFILE_CHECKS
from fontbakery.utils import (
    chars_in_range,
    compute_unicoderange_bits,
    unicoderange_bit_name,
)
from fontbakery.profiles.shared_conditions import is_italic

profile_imports = ("fontbakery.profiles.googlefonts",)
profile = profile_factory(default_section=Section("Google Sans Flex Custom Checks"))

GOOGLESANSFLEX_PROFILE_CHECKS = GOOGLEFONTS_PROFILE_CHECKS + [
    "com.google.fonts/check/googlesansflex/opentype/os2/fsselectionbit7",
    "com.google.fonts/check/googlesansflex/opentype/os2/winascent",
    "com.google.fonts/check/googlesansflex/opentype/os2/windescent",
    "com.google.fonts/check/googlesansflex/opentype/os2/unicode_range_bits",
    "com.google.fonts/check/googlesansflex/vf/fvaraxes",
    "com.google.fonts/check/googlesansflex/vf/fvardefault",
    "com.google.fonts/check/googlesansflex/opentype/global_fu_attributes",
]

# define check ID's in the upstream `universal` profile
# that should be excluded here
excluded_check_ids = (
    "com.google.fonts/check/ftxvalidator_is_available",
    "com.google.fonts/check/dsig",
    "com.google.fonts/check/family/win_ascent_and_descent",  # replaced by custom checks
    "com.google.fonts/check/unwanted_tables",
    "com.google.fonts/check/outline_jaggy_segments",  # too many unactionable warnings
    "com.google.fonts/check/outline_semi_vertical",  # design rather than QA problem
    "com.google.fonts/check/contour_count",  # design rather than QA problem
    "com.adobe.fonts/check/varfont/valid_default_instance_nameids",  # Bogus
    "com.google.fonts/check/varfont/regular_wght_coord",  # Buggy in 0.8.9
    "com.google.fonts/check/varfont/bold_wght_coord",  # Buggy in 0.8.9
)

ATTRIBUTES = {
    "expected_fvar_axes": ["opsz", "wdth", "wght", "ROND"],
    "opsz_axis_default": 18.0,
    "os2_fsselection_bit7": 1,
    "rond_axis_default": 0.0,
    "wdth_axis_default": 100.0,
    "wght_axis_default": 400.0,
}

GS_FONTUNIT_ATTRIBUTES_UPRIGHT = {
    "head.yMax": 1263,
    "head.yMin": -989,
    "hhea.ascender": 966,
    "hhea.descender": -286,
    "hhea.lineGap": 0,
    "OS/2.sTypoAscender": 966,  # set to match hhea metrics values
    "OS/2.sTypoDescender": -286,
    "OS/2.sTypoLineGap": 0,
    "OS/2.usWinAscent": 1323,
    "OS/2.usWinDescent": 1079,
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
    "head.yMin": -955,
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

# ::::::::::::::::::::::::::::::::::::::::::::::::
# Vertical metrics
# ::::::::::::::::::::::::::::::::::::::::::::::::

# OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is set in all fonts
@check(
    id="com.google.fonts/check/googlesansflex/opentype/os2/fsselectionbit7",
    rationale="""
    Confirms that fonts have OS/2.fsSelection bit 7 (USE_TYPO_METRICS) set \
    for typo vertical metrics (instead of win vertical metrics)
    """,
)
def com_google_fonts_check_googlesansflex_opentype_os2_fsselectionbit7(ttFonts):
    """OS/2.fsSelection bit 7 (USE_TYPO_METRICS) is set in all fonts"""
    os2_fsselection_bit7_isset = ATTRIBUTES["os2_fsselection_bit7"] == 1

    found_fail = False
    fail_list = []
    for tt in ttFonts:
        fsselection_int = tt["OS/2"].fsSelection
        fsselection_bit_is_set_test = (fsselection_int & (1 << 7)) != 0
        if fsselection_bit_is_set_test is os2_fsselection_bit7_isset:
            pass
        else:
            found_fail = True
            fail_list.append(tt.reader.file.name)

    if found_fail:
        yield (
            FAIL,
            f"The OS/2.fsSelection bit 7 (USE_TYPO_METRICS) was NOT set "
            f"in the following fonts: {fail_list}.",
        )
    else:
        yield PASS, "The OS/2.fsSelection bit 7 (USE_TYPO_METRICS) was set in all fonts."


# Note: winAscent and winDescent bounds are defined above yMin and below yMax values
# OS/2.winAscent check
@check(
    id="com.google.fonts/check/googlesansflex/opentype/os2/winascent",
    rationale="""
    Confirms that the OS/2.winAscent value is defined above the yMax
    value across the full glyph repertoire.
    """,
)
def com_google_fonts_check_googlesansflex_opentype_os2_winascent(ttFont):
    """OS/2.winAscent is defined above yMax value across the glyph repertoire"""
    if ttFont["head"].yMax >= ttFont["OS/2"].usWinAscent:
        yield (
            FAIL,
            f"The OS/2.usWinAscent value must be larger "
            f"than the head.yMax value.  Received: OS/2.usWinAscent = "
            f"{ttFont['OS/2'].usWinAscent} head.yMax = {ttFont['head'].yMax}",
        )
    else:
        yield PASS, "The OS/2.winAscent definition is appropriate."


# OS/2.winDescent check
@check(
    id="com.google.fonts/check/googlesansflex/opentype/os2/windescent",
    rationale="""
    Confirms that the OS/2.winDescent value is defined below the yMin
    value across the full glyph repertoire.
    """,
)
def com_google_fonts_check_googlesansflex_opentype_os2_windescent(ttFont):
    """OS/2.winDescent is defined below yMin value across the glyph repertoire"""
    # note: WinDescent is expressed as a positive value even though the metric
    # extends below the baseline.  We must use unary neg operation for the
    # comparison here
    if ttFont["head"].yMin <= -ttFont["OS/2"].usWinDescent:
        yield (
            FAIL,
            f"The OS/2.usWinDescent value must be less "
            f"than the head.yMin value.  Received: OS/2.usWinDescent = "
            f"{ttFont['OS/2'].usWinDescent} head.yMin = {ttFont['head'].yMin}",
        )
    else:
        yield PASS, "The OS/2.winDescent value is appropriate."


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


# ::::::::::::::::::::::::::::::::::::::::::::::::
# Other metrics
# ::::::::::::::::::::::::::::::::::::::::::::::::


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
def com_google_fonts_check_googlesansflex_variable_fvar_axes(ttFont):
    """Confirms that the variable font builds include expected axes."""
    tt = ttFont
    observed_axis_list = []
    for axis in tt["fvar"].axes:
        observed_axis_list.append(axis.axisTag)

    if len(observed_axis_list) != len(ATTRIBUTES["expected_fvar_axes"]):
        yield (
            FAIL,
            f"{tt.reader.file.name} does not include the correct axis tags. \n"
            f"Observed: {observed_axis_list}\n"
            f"Expected: {ATTRIBUTES['expected_fvar_axes']}",
        )

    has_all_tags = True
    for axis_tag in ATTRIBUTES["expected_fvar_axes"]:
        if axis_tag in observed_axis_list:
            pass
        else:
            has_all_tags = False
            yield (FAIL, f"{tt.reader.file.name} does not include axis tag {axis_tag}")

    if has_all_tags:
        yield (PASS, f"{tt.reader.file.name} includes all expected axis tags")


@check(
    id="com.google.fonts/check/googlesansflex/vf/fvardefault",
    conditions=["is_variable_font"],
    rationale="""
    Confirms that the variable font format builds include the expected fvar
    default definitions for the Google Sans design axes
    """,
)
def com_google_fonts_check_googlesansflex_variable_fvar_default(ttFont):
    """Confirms that the variable font builds include correct fvar default."""
    tt = ttFont
    expectations = {
        "opsz": ATTRIBUTES["opsz_axis_default"],
        "wdth": ATTRIBUTES["wdth_axis_default"],
        "wght": ATTRIBUTES["wght_axis_default"],
        "ROND": ATTRIBUTES["rond_axis_default"],
    }

    for axis in tt["fvar"].axes:
        tag = axis.axisTag
        if tag in expectations:
            if axis.defaultValue != expectations[tag]:
                yield (
                    FAIL,
                    f"{tt.reader.file.name} does not include the correct "
                    f"fvar {tag} axis default.\n"
                    f"Found: `{axis.defaultValue}` and expected `{expectations[tag]}`",
                )
            else:
                yield (
                    PASS,
                    f"{tt.reader.file.name} contains the expected fvar {tag} default.",
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
