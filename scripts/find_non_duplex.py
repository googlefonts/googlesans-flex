# Copyright 2025 Google Sans Flex authors
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

"""Identifies the exact location of glyphs that accidentally change width across
duplex axes (e.g.  Grade, Roundness)."""

from argparse import ArgumentParser

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

DUPLEX = ("Grade", "Roundness")

type HashableCoords = tuple[tuple[str, float], ...]

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.description = __doc__
    parser.add_argument("designspace", type=DesignSpaceDocument.fromfile)
    args = parser.parse_args()

    # Load UFOs.
    doc = args.designspace
    assert isinstance(doc, DesignSpaceDocument)
    doc.loadSourceFonts(Font.open)

    # Get the widths of each glyph. Indexed by their non-duplex location, then
    # by width as identified by their duplex location.
    widths: dict[str, dict[HashableCoords, dict[float, HashableCoords]]] = {}
    for source in doc.sources:
        assert isinstance(source.font, Font)

        layer = (
            source.font
            if source.layerName is None
            else source.font.layers[source.layerName]
        )

        for glyph in layer:
            assert isinstance(glyph.name, str)

            non_duplex_pos: HashableCoords = tuple(
                (axis.name, source.location[axis.name])  # type: ignore
                for axis in doc.axes
                if axis.name not in DUPLEX
            )
            duplex_pos: HashableCoords = tuple(
                (axis.name, source.location[axis.name])  # type: ignore
                for axis in doc.axes
                if axis.name in DUPLEX
            )

            glyph_widths = widths.setdefault(glyph.name, {})
            at_fixed_loc = glyph_widths.setdefault(non_duplex_pos, {})
            at_fixed_loc[glyph.width] = duplex_pos

    # Print any interesting results.
    for glyph, glyph_widths in widths.items():
        for non_duplex_pos, seen in glyph_widths.items():
            if len(seen) <= 1:
                continue

            print("Glyph:", glyph)
            print("  At:", dict(non_duplex_pos))
            for width, duplex in sorted(seen.items()):
                print("    Duplex:", dict(duplex))
                print("      Width:", width)
            print()
