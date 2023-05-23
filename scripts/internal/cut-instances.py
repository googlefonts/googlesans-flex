# Copyright 2022 Google Sans Authors
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
import subprocess
import sys
from pathlib import Path
from typing import Any

import ufoLib2
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.O_S_2f_2 import Panose
from ufo2ft.fontInfoData import (
    getAttrWithFallback,
    normalizeStringForPostscript,
    intListToNum,
)


def cut_instance(
    variable_font: Path,
    user_location: dict[str, float],
    panose_values: list[int],
    family_name: str | None,
    style_name: str | None,
    stylemap_family_name: str | None,
    stylemap_style_name: str | None,
    output_file: Path,
) -> None:
    user_location_args = [f"{k}={v}" for k, v in user_location.items()]

    # Create output directory in case it doesn't exist yet on CI, when passing
    # artifacts around.
    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"Cutting {user_location_args} from {variable_font}")
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

    panose = Panose()
    panose.bFamilyType = panose_values[0]
    panose.bSerifStyle = panose_values[1]
    panose.bWeight = panose_values[2]
    panose.bProportion = panose_values[3]
    panose.bContrast = panose_values[4]
    panose.bStrokeVariation = panose_values[5]
    panose.bArmStyle = panose_values[6]
    panose.bLetterForm = panose_values[7]
    panose.bMidline = panose_values[8]
    panose.bXHeight = panose_values[9]
    font["OS/2"].panose = panose

    info = {
        "familyName": family_name,
        "styleName": style_name,
        "styleMapFamilyName": stylemap_family_name,
        "styleMapStyleName": stylemap_style_name,
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

    font.save(output_file)


def build_name_entries(info: dict[str, Any], name: Any) -> None:
    info = ufoLib2.objects.Info(**info)

    familyName = getAttrWithFallback(info, "styleMapFamilyName")
    styleName = getAttrWithFallback(info, "styleMapStyleName").title()
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


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "variable_font", type=Path, help="Variable font to cut instances from."
    )
    parser.add_argument(
        "designspace",
        type=DesignSpaceDocument.fromfile,
        help="Designspace to take instances from.",
    )
    parser.add_argument("output_path", type=Path, help="Output path.")
    parsed_args = parser.parse_args(args)
    designspace: DesignSpaceDocument = parsed_args.designspace
    output_path: Path = parsed_args.output_path
    variable_font: Path = parsed_args.variable_font

    instance = next(
        (i for i in designspace.instances if Path(i.filename).stem == output_path.stem),
        None,
    )
    if instance is None:
        parser.error(f"Cannot find instance with stem '{output_path.stem}'.")

    name2tag = {axis.name: axis.tag for axis in designspace.axes}
    name2axis = {axis.name: axis for axis in designspace.axes}
    custom_parameters = dict(instance.lib["com.schriftgestaltung.customParameters"])
    user_location = {
        name2tag[k]: name2axis[k].map_backward(v) for k, v in instance.location.items()
    }

    family_name = custom_parameters.get("preferredFamilyName", instance.familyName)
    style_name = custom_parameters.get("preferredSubfamilyName", instance.styleName)
    stylemap_family_name = instance.styleMapFamilyName
    stylemap_style_name = instance.styleMapStyleName

    cut_instance(
        variable_font,
        user_location,
        custom_parameters["panose"],
        family_name,
        style_name,
        stylemap_family_name,
        stylemap_style_name,
        output_path,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
