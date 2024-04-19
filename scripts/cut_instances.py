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
import subprocess
import sys
from pathlib import Path
from typing import Any, TypedDict

import fontTools.otlLib.optimize.gpos
import ufoLib2
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.O_S_2f_2 import Panose
from fontv.libfv import FontVersion
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


# These are then produced at each weight instance defined in the Designspace
TARGET_INSTANCES: dict[str, WorkspaceInstance] = {
    "Google Sans Flex Normal": {
        "opsz": 144,
        "wdth": 100,
        "ROND": 0,
    },
    "Google Sans Flex UltraCondensed": {
        "opsz": 144,
        "wdth": 50,
        "ROND": 0,
    },
    "Google Sans Flex SuperCondensed": {
        "opsz": 144,
        "wdth": 25,
        "ROND": 0,
    },
    "Google Sans Flex Rounded": {
        "opsz": 144,
        "wdth": 100,
        "ROND": 100,
    },
    "Google Sans Flex Text": {
        "opsz": 12,
        "wdth": 100,
        "ROND": 0,
    },
    "Google Sans Flex ExtraExpanded": {
        "opsz": 144,
        "wdth": 150,
        "ROND": 0,
    },
}

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

    # fudge global font unit attributes as they change for some reason
    os2 = font["OS/2"]
    upm_scale = font["head"].unitsPerEm / 1000
    # before = {attr: getattr(os2, attr) for attr in GS_OS2_ATTRIBUTES_UPRIGHT.keys()}
    if user_location["slnt"] == 0:
        for attr, val in GS_OS2_ATTRIBUTES_UPRIGHT.items():
            assert hasattr(os2, attr), f"don't have {attr}"
            setattr(os2, attr, int(val * upm_scale))
    elif user_location["slnt"] == -10:
        for attr, val in GS_OS2_ATTRIBUTES_ITALIC.items():
            assert hasattr(os2, attr), f"don't have {attr}"
            setattr(os2, attr, int(val * upm_scale))
    # for attr, before_val in before.items():
    #     after_val = int(getattr(os2, attr))
    #     if before_val != after_val:
    #         print(f"{attr}: {before_val} -> {after_val}")

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

    nameVals = {
        1: familyName,
        2: styleName,
        4: fullName,
        6: getAttrWithFallback(info, "postscriptFontName"),
        16: preferredFamilyName,
        17: preferredSubfamilyName,
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
            TARGET_INSTANCES.items(), (False, True)
        ):
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
                        None,  # style_name: str | None
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
