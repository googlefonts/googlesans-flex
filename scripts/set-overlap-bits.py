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
from pathlib import Path
import re

from ufoLib2 import Font
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import _g_l_y_f


def set_overlap_bits_if_overlapping(
    varfont: TTFont, overlapping_glyphs: set[str]
) -> tuple[int, int]:
    glyf_table: _g_l_y_f.table__g_l_y_f = varfont["glyf"]  # type: ignore

    overlapping_contours = 0
    overlapping_components = 0
    for glyph_name in overlapping_glyphs:
        glyph = glyf_table[glyph_name]
        # Set OVERLAP_COMPOUND bit for compound glyphs
        if glyph.isComposite():
            overlapping_components += 1
            glyph.components[0].flags |= _g_l_y_f.OVERLAP_COMPOUND
        # Set OVERLAP_SIMPLE bit for simple glyphs
        elif glyph.numberOfContours > 0:
            overlapping_contours += 1
            glyph.flags[0] |= _g_l_y_f.flagOverlapSimple

    return (overlapping_contours, overlapping_components)


# A glyph name that can have whitespace around it, with an optional comment at
# the end of the line. 1st capture group is the glyph name (with no surrounding
# whitespace)
GLYPHS_LINE = re.compile(r"^\s*([A-z0-9._]+)\s*(#.*)?$")


def parse_line(line: str) -> str | None:
    if match := GLYPHS_LINE.fullmatch(line):
        return match.group(1)
    return None


parser = argparse.ArgumentParser()
parser.add_argument("glyph_list", type=Path)
parser.add_argument("designspace", type=DesignSpaceDocument.fromfile)
parser.add_argument("font", type=Path)
parsed_args = parser.parse_args()
glyph_list_path: Path = parsed_args.glyph_list
designspace: DesignSpaceDocument = parsed_args.designspace
font_path: Path = parsed_args.font

designspace.loadSourceFonts(Font.open)
default_source = designspace.default
name_mapping = default_source.font.lib.get("public.postscriptNames", {})  # type: ignore
glyph_list = {
    name_mapping.get(name, name)
    for line in glyph_list_path.read_text().splitlines()
    if (name := parse_line(line))
}

font = TTFont(font_path)
num_glyphs: int = font["maxp"].numGlyphs  # type: ignore
fvar = font["fvar"]

glyph_order = set(font.getGlyphOrder())
if leftovers := sorted(glyph_list - glyph_order):
    print(f"Glyphs in overlap list not in font {font_path}: {leftovers}")
glyph_list_for_font = glyph_list.intersection(glyph_order)
ocont, ocomp = set_overlap_bits_if_overlapping(font, glyph_list_for_font)
ocont_p = ocont / num_glyphs
ocomp_p = ocomp / num_glyphs
assert font.reader
print(
    font.reader.file.name,
    f"{num_glyphs} glyphs, "
    f"{ocont} overlapping contours ({ocont_p:.2%}), "
    f"{ocomp} overlapping components ({ocomp_p:.2%})",
)
font.save(font_path)
