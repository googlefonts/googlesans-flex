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

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.H_V_A_R_ import table_H_V_A_R_ as Hvar

AxisToTuples = dict[str, set[tuple[float]]]
AxisToCoords = dict[str, set[float]]


def get_interesting_locs(ttf: TTFont, glyph: str) -> tuple[AxisToCoords, AxisToTuples]:
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
    tups = {
        tag: {(tup.StartCoord, tup.PeakCoord, tup.EndCoord) for tup in tuples}
        for tag, tuples in zip(tags, zip(*regions))
    }

    # Summarise the coordinates seen in these tuples.
    interesting_locs = {
        tag: {pos for tup in tuples for pos in tup} for tag, tuples in tups.items()
    }

    return interesting_locs, tups


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("ttf", type=Path)
    args = parser.parse_args()

    assert isinstance(args.ttf, Path)
    ttf = TTFont(args.ttf)

    for glyph in ttf.getGlyphOrder():
        assert isinstance(glyph, str)
        _, tuples = get_interesting_locs(ttf, glyph)

        case_insensitive = re.sub(r"([A-Z])", r"\1_", glyph)

        to_dump = args.ttf.parent / "Glyphs" / f"{case_insensitive}.json"
        to_dump.write_text(
            json.dumps({tag: sorted(tups) for tag, tups in tuples.items()}, indent=2)
        )
