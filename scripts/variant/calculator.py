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
SUBSET: set[int] = set()

SUBSET_BY_NAME = {
    "uni000D",
    "space",
    "exclam",
    "quotedbl",
    "numbersign",
    "dollar",
    "cent",
    "currency",
    "Euro",
    "percent",
    "ampersand",
    "quotesingle",
    "parenleft",
    "parenright",
    "asterisk",
    "plus",
    "comma",
    "hyphen",
    "period",
    "slash",
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "colon",
    "semicolon",
    "less",
    "equal",
    "greater",
    "question",
    "at",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
    "bracketleft",
    "backslash",
    "bracketright",
    "asciicircum",
    "underscore",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "braceleft",
    "bar",
    "braceright",
    "asciitilde",
    "exclamdown",
    "sterling",
    "yen",
    "brokenbar",
    "section",
    "copyright",
    "guillemotleft",
    "logicalnot",
    "uni00AD",
    "registered",
    "degree",
    "plusminus",
    "uni00B2",
    "uni00B3",
    "uni00B5",
    "paragraph",
    "periodcentered",
    "uni00B9",
    "guillemotright",
    "onequarter",
    "onehalf",
    "threequarters",
    "questiondown",
    "multiply",
    "divide",
    "uni03BC",
    "guilsinglleft",
    "guilsinglright",
    "fraction",
    "uni2074",
    "greaterequal",
    "lessequal",
    "approxequal",
    "notequal",
    "zero.denominator",
    "one.denominator",
    "two.denominator",
    "three.denominator",
    "four.denominator",
    "five.denominator",
    "six.denominator",
    "seven.denominator",
    "eight.denominator",
    "nine.denominator",
    "zero.numerator",
    "one.numerator",
    "two.numerator",
    "three.numerator",
    "four.numerator",
    "five.numerator",
    "six.numerator",
    "seven.numerator",
    "eight.numerator",
    "nine.numerator",
    "zero.tf",
    "one.tf",
    "two.tf",
    "three.tf",
    "four.tf",
    "five.tf",
    "six.tf",
    "seven.tf",
    "eight.tf",
    "nine.tf",
    "period.tf",
    "comma.tf",
    "colon.tf",
    "semicolon.tf",
    "numbersign.tf",
    "colon.time",
    "space.tf",
    "cent.tf",
    "currency.tf",
    "dollar.tf",
    "Euro.tf",
    "sterling.tf",
    "plus.tf",
    "minus.tf",
    "multiply.tf",
    "divide.tf",
    "equal.tf",
    "notequal.tf",
    "greater.tf",
    "less.tf",
    "greaterequal.tf",
    "lessequal.tf",
    "plusminus.tf",
    "approxequal.tf",
    "logicalnot.tf",
    "percent.tf",
    "section.tf",
    "zero.slash",
    "zeroslash",
    "zeroslash.tf",
    "quoteright",
    "quoteleft",
    "quotesinglbase",
    "quotedblbase",
    "quotedblleft",
    "quotedblright",
    "bullet",
    "endash",
    "emdash",
    "minus",
    "horizontalelipsis",
    "trademark",
    "uni2003",
    "uni2002",
    "uni2009",
    "uni200A",
    "uni2005",
    "uni2006",
    "uni2004",
    "uni200B",
    "zerosuperscript",
    "onesuperscript",
    "twosuperscript",
    "threesuperscript",
    "foursuperscript",
    "fivesuperscript",
    "sixsuperscript",
    "sevensuperscript",
    "eightsuperscript",
    "ninesuperscript",
    "zerosubscript",
    "onesubscript",
    "twosubscript",
    "threesubscript",
    "foursubscript",
    "fivesubscript",
    "sixsubscript",
    "sevensubscript",
    "eightsubscript",
    "ninesubscript",
    "radical",
    "u1D6E1",
    "notequalslash",
    "greaterequalstroke",
    "uni00A0",
    "uni202F",
    "uni25CC",
    "zero.dnom.percent",
    "_dotsdivide",
    "percentbar.tab",
    "uni207B",
    "multiplysuperior",
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


def subset(ttf: TTFont, codepoints: set[int], glyph_names: set[str]) -> None:
    """Subset to only keep some codepoints, with minimal other changes."""

    options = SubsetOptions()

    # Validate our subsets.
    options.ignore_missing_glyphs = False
    options.ignore_missing_unicodes = False

    # Keep notdef.
    options.notdef_outline = True

    # Do not prune more than our subset requires.
    options.layout_features = ["*"]
    options.name_IDs = ["*"]  # type: ignore # (not just ints)
    options.name_languages = ["*"]  # type: ignore # (not just ints)

    # Leave yMax alone.
    options.recalc_bounds = False

    # This is better than selecting too few.
    options.prune_unicode_ranges = False
    options.prune_codepage_ranges = False
    options.glyph_names = True

    subsetter = Subsetter(options=options)
    subsetter.populate(unicodes=list(codepoints), glyphs=list(glyph_names))
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
    parser.add_argument("ttf", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    ttf = TTFont(args.ttf, recalcBBoxes=False)  # leave yMax alone

    remap_codepoints(ttf, NEW_TO_OLD)
    subset(ttf, SUBSET, SUBSET_BY_NAME)

    ttf.save(args.out)


if __name__ == "__main__":
    main()
