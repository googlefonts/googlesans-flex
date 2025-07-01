# Copyright 2025 Google Sans Flex Authors
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
#
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fonttools",
# ]
# ///

"""
Consumes a TTF, and produces a derived TTF that has the codepoints for Greek and
mathematical Pi swapped, and that is pruned to fewer codepoints.
"""

from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.subset import Subsetter, Options as SubsetOptions


def swap_mapping(ttf: TTFont, first: int, second: int) -> None:
    """Swap the glyphs mapped for two codepoints."""

    mapping = ttf.getBestCmap()
    new = {
        codepoint: (
            mapping[second]
            if codepoint == first
            else mapping[first]
            if codepoint == second
            else glyph
        )
        for codepoint, glyph in mapping.items()
    }

    builder = FontBuilder(font=ttf)
    builder.setupCharacterMap(new)


def subset(ttf: TTFont, codepoints: set[int]) -> None:
    """Subset to only keep some codepoints, with minimal other changes."""

    options = SubsetOptions()

    options.ignore_missing_glyphs = False
    options.ignore_missing_unicodes = False

    options.notdef_outline = True

    options.layout_features = ["*"]

    options.name_IDs = ["*"]  # type: ignore # (not just ints)
    options.name_languages = ["*"]  # type: ignore # (not just ints)

    options.recalc_bounds = True

    options.prune_unicode_ranges = False
    options.glyph_names = True

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=codepoints)
    subsetter.subset(ttf)


def main():
    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser()
    parser.description = """
        Consumes a TTF, and produces a derived TTF that has the codepoints for
        Greek and mathematical Pi swapped, and that is pruned to fewer
        codepoints.
    """
    parser.add_argument("ttf", type=TTFont)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    # TODO: Fill final codepoints to swap, and codepoints to keep.
    ttf = args.ttf

    swap_mapping(ttf, ord("A"), ord("B"))
    subset(ttf, {ord("A"), ord("B")})

    ttf.save(args.out)


if __name__ == "__main__":
    main()
