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

"""
Command line tool that outputs a sorted TSV giving each glyphs contribution in
bytes to the 'gvar' table, for identifying where optimisation is possible.
"""

import math
import os
from argparse import ArgumentParser
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_v_a_r import GVAR_HEADER_SIZE_HEAD, GVAR_HEADER_SIZE_TAIL
from fontTools.ttLib.tables._g_v_a_r import table__g_v_a_r as GVAR
from rich.console import Console
from rich.table import Table


def get_gvar_contribs(ttf: TTFont) -> dict[str, int]:
    """Get the contribution in bytes of each glyph to the 'gvar' table."""

    # Decompile the 'gvar' table.
    gvar = ttf["gvar"]
    assert isinstance(gvar, GVAR)

    # Get the raw bytes that make up the table.
    assert ttf.reader is not None
    data = ttf.reader["gvar"]

    glyphs: list[str] = ttf.getGlyphOrder()  # type: ignore

    # Use internal API to derive offsets.
    # See: https://github.com/fonttools/fonttools/blob/f7ee2503/Lib/fontTools/ttLib/tables/_g_v_a_r.py#L132-L167
    header_size = GVAR_HEADER_SIZE_HEAD + gvar.gid_size + GVAR_HEADER_SIZE_TAIL
    offsets = gvar.decompileOffsets_(
        data[header_size:],
        tableFormat=(gvar.flags & 1),  # type: ignore
        glyphCount=len(glyphs),  # type: ignore
    )
    lengths = {name: offsets[gid + 1] - offsets[gid] for gid, name in enumerate(glyphs)}

    return lengths


def output_csv_report(contribs: dict[str, int], path: Path) -> None:
    """Output a tab-delimited report to the given path."""

    with path.open("w") as output:
        print("Bytes", "Name", sep="\t", file=output)
        for size, glyph in sorted((size, glyph) for glyph, size in contribs.items()):
            print(size, glyph, sep="\t", file=output)


def output_rich_report(
    contribs: dict[str, int], force_terminal: bool | None = None
) -> None:
    """Output a formatted table to stdout with rich."""

    table = Table(title="'gvar' size contribution by glyph")

    table.add_column("Size (bytes)", justify="right")
    table.add_column("Glyph", justify="left")

    # For linear interpolation of row colour by size.
    colours = [
        "green",
        "cyan",
        "yellow",
        "red",
    ]
    least = min(contribs.values())
    most = max(contribs.values())

    for size, glyph in sorted(
        ((size, glyph) for glyph, size in contribs.items()), reverse=True
    ):
        goodness = colours[
            min(
                math.floor((size - least) / (most - least) * len(colours)),
                len(colours) - 1,
            )
        ]
        table.add_row(f"[bold {goodness}]{size:_}", glyph)

    console = Console(force_terminal=force_terminal)
    console.print(table)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("ttf", type=TTFont)
    parser.add_argument("--output", type=Path, required=False, metavar="CSV")
    args = parser.parse_args()

    # Get glyph contributions, and output rich report to stdout.
    contribs = get_gvar_contribs(args.ttf)

    force_terminal = True if "GITHUB_ACTIONS" in os.environ else None
    output_rich_report(contribs, force_terminal=force_terminal)

    # Optionally, write a tab-delimited CSV report too.
    if args.output:
        output_csv_report(contribs, args.output)
