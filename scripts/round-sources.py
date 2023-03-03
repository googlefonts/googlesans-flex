from __future__ import annotations

import argparse

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font
from fontTools.misc.fixedTools import otRound

parser = argparse.ArgumentParser()
parser.add_argument(
    "designspace",
    type=DesignSpaceDocument.fromfile,
    help="The Designspace with sources to round.",
)
parsed_args = parser.parse_args()
designspace: DesignSpaceDocument = parsed_args.designspace

ufos = designspace.loadSourceFonts(Font.open)

for ufo in ufos:
    ufo.kerning = {k: otRound(v) for k, v in ufo.kerning.items()}
    for layer in ufo.layers:
        for glyph in layer:
            if glyph.width is not None:
                glyph.width = otRound(glyph.width)
            if glyph.height is not None:
                glyph.height = otRound(glyph.height)
            for anchor in glyph.anchors:
                anchor.x = otRound(anchor.x)
                anchor.y = otRound(anchor.y)
            for component in glyph.components:
                component.transformation = tuple(
                    otRound(x) for x in component.transformation
                )
            for contour in glyph.contours:
                for point in contour:
                    point.x = otRound(point.x)
                    point.y = otRound(point.y)
    ufo.save()
