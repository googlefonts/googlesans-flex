#!/usr/bin/env python3
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

import argparse
from pathlib import Path

from ufoLib2 import Font
from fontTools.designspaceLib import DesignSpaceDocument

# Defined in USER coordinates.
INSTANCE_LOCATIONS = {
    "Thin": dict(wght=100.0, wdth=100.0),
    "ExtraLight": dict(wght=200.0, wdth=100.0),
    "Light": dict(wght=300.0, wdth=100.0),
    "Regular": dict(wght=400.0, wdth=100.0),
    "Medium": dict(wght=500.0, wdth=100.0),
    "SemiBold": dict(wght=600.0, wdth=100.0),
    "Bold": dict(wght=700.0, wdth=100.0),
    "ExtraBold": dict(wght=800.0, wdth=100.0),
    "Black": dict(wght=900.0, wdth=100.0),
}
POSTSCRIPT_NAMES = "public.postscriptNames"


def main(designspace_path: Path):
    designspace = DesignSpaceDocument.fromfile(designspace_path)
    designspace.loadSourceFonts(Font.open)
    designspace.instances.clear()
    for name, location in INSTANCE_LOCATIONS.items():
        # TODO: Add directly as user coordinates when we adopt DS5.
        as_design_location = designspace.map_forward(location)
        designspace.addInstanceDescriptor(
            styleName=name, designLocation=as_design_location
        )

    designspace.write(designspace_path)

    default_location = designspace.findDefault()

    default_ufo: Font | None = default_location.font
    production_names: dict[str, str]
    if POSTSCRIPT_NAMES not in default_ufo.lib:
        production_names = default_ufo.lib[POSTSCRIPT_NAMES] = {}
    else:
        production_names = default_ufo.lib[POSTSCRIPT_NAMES]

    # Add production names for glyphs that don't have a usable design name
    # Fix any production names that contain disallowed characters
    for glyph in default_ufo:
        if not glyph.name:
            continue
        existing_production_name = production_names.get(glyph.name)
        if existing_production_name is not None:
            if "-" in existing_production_name:
                new_name = existing_production_name.replace("-", "")
                print(
                    f"WARN: {glyph.name}: updated bad postscript name '{existing_production_name}' to '{new_name}'"
                )
                production_names[glyph.name] = new_name
        elif "-" in glyph.name:
            new_name = glyph.name.replace("-", "")
            print(f"INFO {glyph.name}: adding postscript name '{new_name}'")
            production_names[glyph.name] = new_name
    for source in designspace.sources:
        if source.layerName is not None:
            continue
        ufo: Font = source.font
        ufo.info.copyright = "Copyright 2015 Google LLC. All Rights Reserved."
        ufo.info.familyName = "Google Sans Flex"
        if source is default_location:
            ufo.info.styleName = "Regular"
            ufo.info.openTypeOS2Panose = [2, 11, 5, 3, 3, 5, 2, 4, 2, 4]
        ufo.info.trademark = "Google Sans is a trademark of Google."
        ufo.info.openTypeNameManufacturer = "Google LLC"
        ufo.info.openTypeNameDesigner = "Google Sans Authors"
        ufo.info.openTypeNameDesignerURL = "https://design.google"
        ufo.info.openTypeNameLicense = "Google offers many fonts on open source terms. Google Sans Flex is not one of them. Please see google.com/fonts for alternatives."
        # TODO: get version from config.yaml once supported
        ufo.info.versionMajor = 1
        ufo.info.versionMinor = 0

        # Clear out export bans to avoid confusion.
        ufo.lib["public.skipExportGlyphs"] = []

        # Production names are based on the default source.
        ufo.lib[POSTSCRIPT_NAMES] = production_names


        ufo.save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("designspace", type=Path)
    parsed_args = parser.parse_args()
    main(parsed_args.designspace)
