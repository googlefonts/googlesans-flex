# Copyright 2024 Google Sans Flex authors
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

"""Get the location tuples that contribute to a glyph's HVAR."""

from __future__ import annotations

import json
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import Literal

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.H_V_A_R_ import table_H_V_A_R_ as Hvar
from fontTools.ttLib.tables._g_v_a_r import table__g_v_a_r as Gvar
from fontTools.ttLib.tables._g_l_y_f import table__g_l_y_f as Glyf
from fontTools.ttLib.tables.TupleVariation import TupleVariation


def get_interesting_locs(
    ttf: TTFont, glyph: str, table: Literal["HVAR", "gvar"], recursive: bool
) -> dict[str, set[tuple[float]]]:

    if table == "HVAR":
        hvar: Hvar = ttf["HVAR"]

        # Follow the mapping to get the glyph's variation.
        varidx = hvar.table.AdvWidthMap.mapping[glyph]
        major, _minor = varidx >> 16, varidx & 0xFFFF
        data = hvar.table.VarStore.VarData[major]

        # Follow the region indices to get the glyph's regions.
        regions = [
            hvar.table.VarStore.VarRegionList.Region[idx].VarRegionAxis
            for idx in data.VarRegionIndex
        ]

        tags = [axis.axisTag for axis in ttf["fvar"].axes]

        # Fetch the location tuples for each axis.
        tups: dict[str, set[tuple[float]]] = {
            tag: {(tup.StartCoord, tup.PeakCoord, tup.EndCoord) for tup in tuples}
            for tag, tuples in zip(tags, zip(*regions))
        }
    elif table == "gvar":
        gvar: Gvar = ttf["gvar"]

        variations: list[TupleVariation] = gvar.variations[glyph]

        tups: dict[str, set[tuple[float]]] = {}
        for tv in variations:
            for tag, tup in tv.axes.items():
                tups.setdefault(tag, set()).add(tup)

    if recursive:
        glyf: Glyf = ttf["glyf"]
        outlines = glyf[glyph]

        if outlines.isComposite():
            children = {comp.glyphName for comp in outlines.components}
            for child in children:
                child_locs = get_interesting_locs(ttf, child, table, True)
                for child_tag, child_tups in child_locs.items():
                    tups.setdefault(child_tag, set()).update(child_tups)

    return tups


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("ttf", type=Path)
    parser.add_argument("table", choices=["HVAR", "gvar"])
    parser.add_argument("--recursive", action="store_true")
    args = parser.parse_args()

    assert isinstance(args.ttf, Path)
    ttf = TTFont(args.ttf)

    for glyph in ttf.getGlyphOrder():
        assert isinstance(glyph, str)
        tuples = get_interesting_locs(ttf, glyph, args.table, args.recursive)

        case_insensitive = re.sub(r"([A-Z])", r"\1_", glyph)

        to_dump = args.ttf.parent / "Glyphs" / f"{case_insensitive}.json"
        to_dump.write_text(
            json.dumps(
                {tag: sorted(tups) for tag, tups in sorted(tuples.items())}, indent=2
            )
        )
