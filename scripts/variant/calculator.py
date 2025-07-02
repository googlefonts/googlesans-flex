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
Accepts a TTF, and produces a derived TTF that is subset and has codepoints
reassigned as appropriate for calculator usage.

(Configured with the globals below.)

Usage (automatically install dependencies):
    `$ uv run --script calculator.py in.ttf --out out.ttf`

Usage (manually install dependencies):
    1. Install Python (only tested with 3.13)
    2. Install `fonttools`
    3. `$ python calculator.py in.ttf --out out.ttf`
"""

from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.subset import Subsetter, Options as SubsetOptions

#####################
### Configuration ###
#####################

# The 'key' codepoint will be remapped to the glyph of the 'value' codepoint.
# TODO: Tinker with and configure as required.
NEW_TO_OLD = {
    # Map 'Greek Small Letter Pi' to the glyph at 'Mathematical Bold Pi Symbol'
    ord("π"): ord("𝛡")
}

# Only the following codepoints and their descendent glyphs will be kept.
# TODO: Tinker with and configure as required.
SUBSET = {
    ord("0"),
    ord("1"),
    ord("2"),
    ord("3"),
    ord("4"),
    ord("5"),
    ord("6"),
    ord("7"),
    ord("8"),
    ord("9"),
    ord("π"),
}

############
### Code ###
############


def remap_codepoints(ttf: TTFont, new_to_old: dict[int, int]) -> None:
    """Redirect codepoints to glyphs at other existing codepoints."""

    existing = ttf.getBestCmap()
    overrides = {new: existing[old] for new, old in new_to_old.items()}

    combined = {**existing, **overrides}

    builder = FontBuilder(font=ttf)
    builder.setupCharacterMap(combined)


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
    options.prune_codepage_ranges = False
    options.glyph_names = True

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=list(codepoints))
    subsetter.subset(ttf)


def main():
    from argparse import ArgumentParser
    from pathlib import Path

    parser = ArgumentParser()
    parser.description = """
        Accepts a TTF, and produces a derived TTF that is subset and has
        codepoints reassigned as appropriate for calculator usage.

        (Configured with the globals at the top of the file.)
    """
    parser.add_argument("ttf", type=TTFont)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    ttf = args.ttf

    remap_codepoints(ttf, NEW_TO_OLD)
    subset(ttf, SUBSET)

    ttf.save(args.out)


if __name__ == "__main__":
    main()
