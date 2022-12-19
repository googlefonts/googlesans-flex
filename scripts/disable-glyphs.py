from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

parser = argparse.ArgumentParser()
parser.add_argument("designspace", type=Path, help="The Designspace to use.")
parser.add_argument("glyph", nargs="+", help="The glyphs to ignore when compiling.")
parsed_args = parser.parse_args()
skip_export_glyphs: list[str] = parsed_args.glyph

designspace = DesignSpaceDocument.fromfile(parsed_args.designspace)
ufos = designspace.loadSourceFonts(Font.open)

for ufo in ufos:
    ufo.lib["public.skipExportGlyphs"] = skip_export_glyphs
    ufo.save()
