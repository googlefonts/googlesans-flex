#!/usr/bin/env python3
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

from pathlib import Path

from fontTools.unicodedata import normalize
from ufoLib2 import Font

# Copied from current feature file
# Maybe not needed?
# CombiningTopAccents = [
#     "gravecomb",
#     "acutecomb",
#     "circumflexcomb",
#     "tildecomb",
#     "macroncomb",
#     "brevecomb",
#     "dotaccentcomb",
#     "dieresiscomb",
#     "ringcomb",
#     "hungarumlautcomb",
#     "caroncomb",
#     "commaturnedabovecomb",
# ]


def main():
    ufo_path = next(Path("sources").glob("*.ufo"))
    font = Font.open(ufo_path)
    cmap = {}
    precomposed = []
    for glyph in font:
        for code_point in glyph.unicodes:
            cmap[code_point] = glyph.name
            nfd = normalize("NFD", chr(code_point))
            if len(nfd) >= 2:
                precomposed.append((glyph.name, nfd))

    ccmp = [
        "lookup ccmp_top_accents {",
        "  lookupflag UseMarkFilteringSet @CombiningTopAccents;",
    ]
    errors = []
    for glyph, decomposed in sorted(precomposed):
        try:
            comment = glyph in font.lib.get("public.skipExportGlyphs", [])
            if comment:
                ccmp.append(f"  # {glyph} isn't currently exported")
            ccmp.append(
                f" {' #' if comment else ''} sub {glyph}' @CombiningTopAccents by {' '.join(cmap[ord(part_code_point)] for part_code_point in decomposed)};"
            )
        except KeyError:
            errors.append(f"# Error: No ccmp for {glyph}")
    ccmp.append("} ccmp_top_accents;")

    print("\n".join(ccmp))
    print("\n".join(errors))

    print("Insert the above by hand into the Glyphs.app source file, then test")
    print("Generated based on", ufo_path)


if __name__ == "__main__":
    main()
