import argparse
from pathlib import Path

from ufoLib2 import Font
from fontTools.designspaceLib import DesignSpaceDocument

parser = argparse.ArgumentParser()
parser.add_argument("designspace", type=Path)
parsed_args = parser.parse_args()
designspace_path: Path = parsed_args.designspace
designspace = DesignSpaceDocument.fromfile(designspace_path)
ufos: list[Font] = designspace.loadSourceFonts(Font.open)

instance_locations = {
    "Thin": dict(wght=100.0),
    "ExtraLight": dict(wght=200.0),
    "Light": dict(wght=300.0),
    "Regular": dict(wght=400.0),
    "Medium": dict(wght=500.0),
    "SemiBold": dict(wght=600.0),
    "Bold": dict(wght=700.0),
    "ExtraBold": dict(wght=800.0),
    "Black": dict(wght=900.0),
}

designspace.instances.clear()
for name, location in instance_locations.items():
    designspace.addInstanceDescriptor(styleName=name, location=location)

designspace.write(designspace_path)

default_location = designspace.findDefault()
for source in designspace.sources:
    if source.layerName is not None:
        continue
    ufo: Font = source.font
    ufo.info.copyright = "Copyright 2015 Google LLC. All Rights Reserved."
    ufo.info.familyName = "Google Sans Flex"
    if source is default_location:
        ufo.info.styleName = "Regular"
    ufo.info.trademark = "Google Sans is a trademark of Google."
    ufo.info.openTypeNameManufacturer = "Google LLC"
    ufo.info.openTypeNameDesigner = "Google Sans Authors"
    ufo.info.openTypeNameDesignerURL = "https://design.google"
    ufo.info.openTypeNameLicense = "Google offers many fonts on open source terms. Google Sans Flex is not one of them. Please see google.com/fonts for alternatives."
    ufo.save()
