# Copyright 2024 Google Sans Flex authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import argparse
import itertools
import multiprocessing
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, TypedDict

import fontTools.otlLib.optimize.gpos
import ufoLib2
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables.O_S_2f_2 import Panose
from fontv.libfv import FontVersion
from gftools.fix import fix_fvar_instances
from prune_font_binary import main as prune_font_binary_main
from ufo2ft.fontInfoData import (
    getAttrWithFallback,
    intListToNum,
    normalizeStringForPostscript,
)


class GoogleSansFlexInstance(TypedDict):
    wght: float | str
    wdth: int | str
    opsz: int | str
    GRAD: int | str
    ROND: int | str
    slnt: int | str


class WorkspaceInstance(TypedDict):
    opsz: int
    wdth: int
    ROND: int


class GoogleTVInstance(TypedDict):
    wght: float | str
    opsz: int
    wdth: int
    ROND: int


# TO DO: limit features to: "tnum,numr,subs,sups,frac,ordn,dnom,zero,kern,locl,mark,mkmk,ccmp,liga"
# TO DO: limit character set to --unicodes="U+D-25CC,U+FB00-1D61E" but retain outlined of the .notdef
# TO DO: output file name: GoogleSansFlexTVSubset.ttf

# These are then produced in upright & italic flavours, retaining only the
# weight variable axis
TARGET_INSTANCES: list[tuple[str, WorkspaceInstance | GoogleTVInstance]] = [
    (
        "Google Sans Flex Normal",
        {
            "opsz": 18,
            "wdth": 100,
            "ROND": 0,
        },
    ),
    (
        "Google Sans Flex Text",
        {
            "opsz": 14,
            "wdth": 100,
            "ROND": 0,
        },
    ),
    (
        "Google Sans Flex Text Fine",
        {
            "opsz": 11,
            "wdth": 100,
            "ROND": 0,
        },
    ),
    (
        "Google Sans Flex Rounded",
        {
            "opsz": 18,
            "wdth": 100,
            "ROND": 100,
        },
    ),
    (
        "Google Sans Flex SemiRounded",
        {
            "opsz": 18,
            "wdth": 100,
            "ROND": 40,
        },
    ),
    (
        "Google Sans Flex UltraCondensed",
        {
            "opsz": 18,
            "wdth": 50,
            "ROND": 0,
        },
    ),
    (
        "Google Sans Flex SuperCondensed",
        {
            "opsz": 18,
            "wdth": 25,
            "ROND": 0,
        },
    ),
    (
        "Google Sans Flex ExtraExpanded",
        {
            "opsz": 18,
            "wdth": 150,
            "ROND": 0,
        },
    ),
    # This slice is then produced in upright & italic flavours, retaining only
    # the weight variable axis in values 400-700 with 400 at default
    (
        "Google Sans Flex TV",
        {
            "wght": "400:400:700",
            "opsz": 18,
            "wdth": 100,
            "ROND": 100,
        },
    ),
]


# Global Google Sans attributes, in 1000 upM font units.
# These need to be kept in sync with qa/check-googlesans.py to avoid FB fails
GS_OS2_ATTRIBUTES_UPRIGHT = {
    "sTypoAscender": 966,  # set to match hhea metrics values
    "sTypoDescender": -286,
    "sTypoLineGap": 0,
    "yStrikeoutPosition": 306,
    "yStrikeoutSize": 84,
    "ySubscriptXOffset": 0,
    # Commented out values have been intentionally changed
    # "ySubscriptXSize": 650,
    # "ySubscriptYOffset": 75,
    "ySubscriptYSize": 600,
    "ySuperscriptXOffset": 0,
    # "ySuperscriptXSize": 650,
    # "ySuperscriptYOffset": 350,
    "ySuperscriptYSize": 600,
}
GS_OS2_ATTRIBUTES_ITALIC = {
    **GS_OS2_ATTRIBUTES_UPRIGHT,
    "ySubscriptXOffset": -13,
    "ySuperscriptXOffset": 62,
}


def cut_instance(
    variable_font: Path,
    user_location: GoogleSansFlexInstance,
    family_name: str | None,
    style_name: str | None,
    output_file: Path,
) -> None:
    user_location_args = [f"{k}={v}" for k, v in user_location.items()]

    with TemporaryDirectory() as tmpdir:
        # HACK: for the SemiRounded, add a STAT entry for that name before slicing
        if user_location["ROND"] == 40:
            vf = TTFont(variable_font)
            stat = vf["STAT"]
            for rondIndex, rond in enumerate(stat.table.DesignAxisRecord.Axis):
                if rond.AxisTag == "ROND":
                    break
            else:
                raise RuntimeError("Cannot find axis ROND")

            axisValRec = ot.AxisValue()
            axisValRec.AxisIndex = rondIndex
            axisValRec.Flags = 0
            axisValRec.ValueNameID = vf["name"].addName("SemiRounded")
            axisValRec.Value = 40
            axisValRec.Format = 1
            stat.table.AxisValueArray.AxisValue.append(axisValRec)

            # Save to a temp file and use that as input for the next step
            tmpfile = Path(tmpdir) / variable_font.name
            vf.save(tmpfile)
            variable_font = tmpfile

        # https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/varLib/instancer/__init__.py
        subprocess.check_call(
            [
                "fonttools",
                "varLib.instancer",
                "--quiet",
                "--remove-overlaps",
                "--update-name-table",
                "-o",
                str(output_file),
                str(variable_font),
                *user_location_args,
            ]
        )

    font = TTFont(output_file)

    font["OS/2"].recalcAvgCharWidth(font)

    font["OS/2"].panose = generate_panose_entries(user_location)

    info = {
        "familyName": family_name,
        "styleName": style_name,
    }
    build_name_entries(info, font["name"])

    # style mapping
    styleMapStyleName = font["name"].getName(2, 3, 1, 0x409).toStr().lower()
    macStyle = []
    if styleMapStyleName == "bold":
        macStyle = [0]
    elif styleMapStyleName == "bold italic":
        macStyle = [0, 1]
    elif styleMapStyleName == "italic":
        macStyle = [1]
    font["head"].macStyle = intListToNum(macStyle, 0, 16)

    selection = font["OS/2"].fsSelection
    selection &= ~(1 << 0)
    selection &= ~(1 << 5)
    selection &= ~(1 << 6)
    if styleMapStyleName == "regular":
        selection |= 1 << 6
    elif styleMapStyleName == "bold":
        selection |= 1 << 5
    elif styleMapStyleName == "italic":
        selection |= 1 << 0
    elif styleMapStyleName == "bold italic":
        selection |= 1 << 0
        selection |= 1 << 5
    font["OS/2"].fsSelection = selection

    is_italic = user_location["slnt"] != 0

    # fudge global font unit attributes as they change for some reason
    os2 = font["OS/2"]
    upm_scale = font["head"].unitsPerEm / 1000
    # before = {attr: getattr(os2, attr) for attr in GS_OS2_ATTRIBUTES_UPRIGHT.keys()}
    if is_italic:
        for attr, val in GS_OS2_ATTRIBUTES_ITALIC.items():
            assert hasattr(os2, attr), f"don't have {attr}"
            setattr(os2, attr, int(val * upm_scale))
    else:
        for attr, val in GS_OS2_ATTRIBUTES_UPRIGHT.items():
            assert hasattr(os2, attr), f"don't have {attr}"
            setattr(os2, attr, int(val * upm_scale))
    # for attr, before_val in before.items():
    #     after_val = int(getattr(os2, attr))
    #     if before_val != after_val:
    #         print(f"{attr}: {before_val} -> {after_val}")

    # Restore weight instances if they were pruned in slicing.
    fix_fvar_instances(font)

    add_STAT_ital(font, is_italic)
    remove_STAT_useless_axes(font, is_italic)

    font.save(output_file)


def build_name_entries(info: dict[str, Any], name: Any) -> None:
    info = ufoLib2.objects.Info(**info)

    familyName = getAttrWithFallback(info, "styleMapFamilyName")
    styleName = getAttrWithFallback(info, "styleMapStyleName").title()
    # Manually fix ufo2ft's output
    if familyName.endswith(" Italic"):
        familyName = familyName[: -len(" Italic")]
        assert " Bold" not in familyName, "build_name_entries can't handle this yet"
        styleName = "Italic"

    preferredFamilyName = getAttrWithFallback(info, "openTypeNamePreferredFamilyName")
    preferredSubfamilyName = getAttrWithFallback(
        info, "openTypeNamePreferredSubfamilyName"
    )
    fullName = f"{preferredFamilyName} {preferredSubfamilyName}"

    # Name 25 must be different for each VF file
    name25 = re.sub(r"[^a-zA-Z]", "", fullName)

    nameVals = {
        1: familyName,
        2: styleName,
        4: fullName,
        6: getAttrWithFallback(info, "postscriptFontName"),
        16: preferredFamilyName,
        17: preferredSubfamilyName,
        25: name25,
    }

    # don't add typographic names if they are the same as the legacy ones
    if nameVals[1] == nameVals[16]:
        del nameVals[16]
        name.removeNames(nameID=16, platformID=3, platEncID=1, langID=0x409)
    if nameVals[2] == nameVals[17]:
        del nameVals[17]
        name.removeNames(nameID=17, platformID=3, platEncID=1, langID=0x409)
    # postscript font name
    if nameVals[6]:
        nameVals[6] = normalizeStringForPostscript(nameVals[6])

    for nameId in sorted(nameVals.keys()):
        nameVal = nameVals[nameId]
        if not nameVal:
            continue
        platformId = 3
        platEncId = 1
        langId = 0x409
        name.setName(nameVal, nameId, platformId, platEncId, langId)


def generate_panose_entries(location: GoogleSansFlexInstance) -> Panose:
    """Generates PANOSE values based on location

    Logic explained here: https://github.com/googlefonts/googlesans-flex/issues/903#issuecomment-2015273322
    """
    WIDTH_PROPORTION = {
        150: 5,
        100: 3,
        50: 7,
        25: 8,
    }

    panose = Panose()
    panose.bFamilyType = 2
    panose.bSerifStyle = 11 if location["ROND"] == 0 else 15
    panose.bWeight = 0
    panose.bProportion = WIDTH_PROPORTION[location["wdth"]]
    panose.bContrast = 3
    panose.bStrokeVariation = 5
    panose.bArmStyle = 2
    panose.bLetterForm = 4 if location["slnt"] == 0 else 11
    panose.bMidline = 2
    panose.bXHeight = 4
    # print(vars(panose))
    return panose


def add_STAT_ital(font: TTFont, is_italic: bool) -> None:
    """Add an ital axis to STAT to link the separate files for uprights and italics.

    The STAT already has a slnt axis, but that doesn't work to link to separate VFs.

    Turn the slnt entry into ital, to appease the Fontbakery check
    `com.google.fonts/check/italic_axis_in_stat`
    """
    stat = font["STAT"]
    for slntIndex, slnt in enumerate(stat.table.DesignAxisRecord.Axis):
        if slnt.AxisTag == "slnt":
            break
    else:
        raise RuntimeError("Cannot find axis slnt")

    slnt.AxisTag = "ital"
    # Find the "Slant" name in the name table and change to "Italic"
    for name in font["name"].names:
        if name.nameID == slnt.AxisNameID:
            name.string = "Italic"

    # Find the "-10" value and change it to "1"
    if is_italic:
        for minusTen in stat.table.AxisValueArray.AxisValue:
            if minusTen.AxisIndex == slntIndex and minusTen.Value == -10:
                minusTen.Value = 1
                break
        else:
            raise RuntimeError("Cannot find -10 slant value")
    else:
        for minusTen in stat.table.AxisValueArray.AxisValue:
            if minusTen.AxisIndex == slntIndex and minusTen.LinkedValue == -10:
                minusTen.LinkedValue = 1
                break
        else:
            raise RuntimeError("Cannot find -10 slant value")


def remove_STAT_useless_axes(font: TTFont, is_italic: bool) -> None:
    """Remove axes other than Weight and Italic, because they're not used
    in this Workspace family.

    See https://github.com/googlefonts/googlesans-flex/issues/949
    """
    stat = font["STAT"]
    # Map from old index to new index or None (deleted)
    new_axis_indices = {}
    new_axes = []
    for index, axis in enumerate(stat.table.DesignAxisRecord.Axis):
        if axis.AxisTag in ("wght", "ital"):
            new_axis_indices[index] = len(new_axes)
            new_axes.append(axis)

    # Code inspired from https://github.com/fonttools/fonttools/blob/main/Lib/fontTools/otlLib/builder.py#L2799
    stat.table.DesignAxisRecord.Axis = new_axes
    stat.table.DesignAxisCount = len(new_axes)

    # Now filter the axis values to keep only those of kept axes, and remap indices
    new_axis_values = []
    for value in stat.table.AxisValueArray.AxisValue:
        new_axis_index = new_axis_indices.get(value.AxisIndex)
        if new_axis_index is not None:
            value.AxisIndex = new_axis_index
            new_axis_values.append(value)

    stat.table.AxisValueArray.AxisValue = new_axis_values
    stat.table.AxisValueCount = len(new_axis_values)


def fontv_sha1(ttf_path: Path) -> None:
    fv = FontVersion(ttf_path)
    fv.set_state_git_commit_sha1()


def otlib_optimise_gpos(ttf_path: Path) -> None:
    ttf = TTFont(ttf_path)
    fontTools.otlLib.optimize.gpos.compact(ttf, 5)


def cut_then_post_process(cut_instance_args: list[Any]) -> None:
    ttf_path: Path = cut_instance_args[-1]

    print(f"Cutting {ttf_path.name}")
    cut_instance(*cut_instance_args)

    print(f"Pruning {ttf_path.name}")
    prune_font_binary_main([str(ttf_path)])

    print(f"Running font-v on {ttf_path.name}")
    fontv_sha1(ttf_path)

    print(f"Running otlLib GPOS optimisation on {ttf_path.name}")
    otlib_optimise_gpos(ttf_path)


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Cut workspace statics (not designspace static instances!) from the big VF",
    )
    parser.add_argument(
        "variable_font", type=Path, help="Variable font to cut instances from."
    )
    parser.add_argument("output_dir", type=Path, help="Output directory.")
    parsed_args = parser.parse_args(args)
    output_dir: Path = parsed_args.output_dir
    variable_font: Path = parsed_args.variable_font

    output_dir.mkdir(parents=True, exist_ok=True)

    with multiprocessing.Pool() as pool:
        for (family_name, workspace_instance), italic in itertools.product(
            TARGET_INSTANCES, (False, True)
        ):
            if family_name == "Google Sans Flex TV" and italic:
                continue  # We want the uprights only.

            coordinates: GoogleSansFlexInstance = {
                # Restrict weight axis to between 100 & 900, default to 400
                "wght": "100:400:900",
                "slnt": -10 if italic else 0,
                "GRAD": 0,
                **workspace_instance,
            }

            ttf_name = (
                family_name.replace(" ", "")
                + ("-Italic" if italic else "")
                + "[wght].ttf"
            )
            ttf_path = output_dir / ttf_name

            pool.apply_async(
                cut_then_post_process,
                (
                    # cut_instance args
                    [
                        variable_font,  # variable_font: Path
                        coordinates,  # user_location: GoogleSansFlexInstance
                        family_name,  # family_name: str | None
                        "Italic" if italic else None,  # style_name: str | None
                        ttf_path,  # output_file: Path
                    ],
                ),
                error_callback=lambda err: print(f"cut_then_post_process error: {err}"),
            )
        pool.close()
        pool.join()

    return 0


if __name__ == "__main__":
    sys.exit(main())
