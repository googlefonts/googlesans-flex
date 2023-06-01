"""Some editor may write out guidelines in a newer format than libs can handle,
so drop them."""

import argparse
import plistlib
from pathlib import Path

import lxml.etree as et
from ufoLib2 import Font

parser = argparse.ArgumentParser()
parser.add_argument("source_path", type=Path)
parsed_args = parser.parse_args()
source_path: Path = parsed_args.source_path

# Fill in missing guideline attributes.
for path in source_path.glob("**/*.ufo"):
    fontinfo_path = path / "fontinfo.plist"
    if fontinfo_path.exists():
        fontinfo = plistlib.loads(fontinfo_path.read_bytes())
        for guideline in fontinfo.get("guidelines", []):
            guideline["x"] = guideline.get("x", 0)
            guideline["y"] = guideline.get("y", 0)
            guideline["angle"] = guideline.get("angle", 0)
        fontinfo_path.write_bytes(plistlib.dumps(fontinfo))

    for glif_path in path.glob("glyphs*/*.glif"):
        glif = et.fromstring(glif_path.read_bytes())
        for guideline in glif.xpath("//guideline"):
            attrib = guideline.attrib
            attrib["x"] = attrib.get("x", "0")
            attrib["y"] = attrib.get("y", "0")
            attrib["angle"] = attrib.get("angle", "0")
        glif_path.write_bytes(et.tostring(glif))

# Normalize.
for path in source_path.glob("**/*.ufo"):
    ufo = Font.open(path)
    for layer in ufo.layers:
        for glyph in layer:
            pass
    ufo.save()
