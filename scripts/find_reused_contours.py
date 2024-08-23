# Copyright 2024 Google Sans Flex Authors
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

"""
Rough script to detect similar contours across glyphs, to show where components
may reduce file size.
"""

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font
from ufoLib2.objects import Contour, Font, Layer


def get_layers(doc: DesignSpaceDocument) -> list[Layer]:
    return [
        (
            source.font.layers.defaultLayer  # type: ignore
            if source.layerName is None
            else source.font.layers[source.layerName]  # type: ignore
        )
        for source in doc.sources
    ]


def normalise_contour(contour: Contour):
    bounds = contour.getBounds()
    assert bounds is not None

    # TODO: Reorder as well

    return tuple(
        [
            (
                precision(point.x - bounds.xMin, 20),
                precision(point.y - bounds.yMin, 20),
                point.type,
                point.smooth,
            )
            for point in contour
        ]
    )


def precision(n: float, precision: float) -> float:
    return (n // precision) * precision


def main(doc: DesignSpaceDocument):
    layers = get_layers(doc)
    unexported = set(doc.lib.get("public.skipExportGlyphs", []))
    glyphs = {glyph for layer in layers for glyph in layer.keys()} - unexported

    by_glyph: dict[tuple, set[tuple[str, int]]] = {}
    for glyph_name in sorted(glyphs):
        print(glyph_name)

        outlines = [
            glyph for layer in layers if (glyph := layer.get(glyph_name)) is not None
        ]

        (length,) = {len(outline) for outline in outlines}

        # TODO: Maybe only include fully additive outlines

        for contour_idx in range(length):
            normalised = tuple(
                normalise_contour(outline[contour_idx]) for outline in outlines
            )
            if glyph_name in {"f", "flig5"}:
                import json

                json.dump(normalised, open(f"{glyph_name}_{contour_idx}.json", "w"))

            by_glyph.setdefault(normalised, set()).add((glyph_name, contour_idx))

    for points, glyphs in by_glyph.items():
        if len(glyphs) == 1:
            continue
        print(len(glyphs), len(points[0]), sorted(glyphs), sep="\t")


if __name__ == "__main__":
    doc = DesignSpaceDocument.fromfile("sources/GoogleSansFlex.designspace")
    doc.loadSourceFonts(Font.open)
