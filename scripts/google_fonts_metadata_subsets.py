#!/usr/bin/env python3
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

import sys
import unicodedata as uni
from argparse import ArgumentParser

from fontTools.ttLib import TTFont
from gfsubsets import CodepointsInSubset, ListSubsets


def main(font: TTFont, missing_codepoints: bool) -> None:
    universe = set(font.getBestCmap().keys())

    known_subsets = ListSubsets()

    subsets = []
    for subset in known_subsets:
        cps = CodepointsInSubset(subset, unique_glyphs=True)
        subsets.append((subset, set(cps)))

    
    res = set()
    while universe:
        best = set()
        best_name = ""
        for subset, cps in subsets:
            if len(universe & cps) > len(best):
                best_name, best = subset, cps
        if len(best) == 0:
            break
        universe -= best
        res.add(best_name)

    for subset in sorted(res):
        print(f"subset: {subset}")

    if missing_codepoints and len(universe) > 0:
        print(f"codepoints not covered: {len(universe)}", file=sys.stderr)
        for char in universe:
            print(f"U+{char:04X} {uni.name(chr(char), '')}", file=sys.stderr)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "ttf",
        type=TTFont,
    )
    parser.add_argument(
        "--missing-codepoints",
        help="list codepoints not covered that are in the listed subsets",
        action="store_true",
    )

    args = parser.parse_args()
    main(args.ttf, args.missing_codepoints)  # type: ignore
