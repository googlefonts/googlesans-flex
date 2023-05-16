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

import pathops
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import _g_l_y_f


def overlapping_glyphs(
    font: hb.Font, coordinates: list[dict[str, float]], num_glyphs: int
) -> set[int]:
    """Return the set of glyph IDs that overlap in any of the user
    coordinates."""
    overlapping = set()
    for gid in range(num_glyphs):
        for coordinate in coordinates:
            font.set_variations(coordinate)
            path = pathops.Path()
            font.draw_glyph_with_pen(gid, path.getPen())
            # Remove overlaps (and do some other stuff):
            path2 = pathops.simplify(path, clockwise=path.clockwise)
            if path != path2:
                overlapping.add(gid)
                break  # If the glyph overlaps in one place, the bit must be set for all.
    return overlapping


def set_overlap_bits_if_overlapping(
    varfont: TTFont, overlapping_glyphs: set[int]
) -> tuple[int, int]:
    name_mapping = varfont.getGlyphNameMany(overlapping_glyphs)
    glyf_table: _g_l_y_f.table__g_l_y_f = varfont["glyf"]

    overlapping_contours = 0
    overlapping_components = 0
    for glyph_name in name_mapping:
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


parser = argparse.ArgumentParser()
parser.add_argument("font", nargs="+", type=Path)
parsed_args = parser.parse_args()
fonts: list[Path] = parsed_args.font

for font_path in fonts:
    font = TTFont(font_path)
    num_glyphs = font["maxp"].numGlyphs
    fvar = font["fvar"]

    instance_coordinates = [instance.coordinates for instance in fvar.instances]
    hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(font_path)))
    overlapping_glyphs = overlapping_glyphs(hbfont, instance_coordinates, num_glyphs)

    ocont, ocomp = set_overlap_bits_if_overlapping(font, overlapping_glyphs)
    ocont_p = ocont / num_glyphs
    ocomp_p = ocomp / num_glyphs
    print(
        font.reader.file.name,
        f"{num_glyphs} glyphs, "
        f"{ocont} overlapping contours ({ocont_p:.2%}), "
        f"{ocomp} overlapping components ({ocomp_p:.2%})",
    )
    font.save(font_path)
