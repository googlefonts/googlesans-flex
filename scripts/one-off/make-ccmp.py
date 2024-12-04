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
    test_chars = []
    for glyph in font:
        for code_point in glyph.unicodes:
            cmap[code_point] = glyph.name
            nfd = [*normalize("NFD", chr(code_point))]
            if len(nfd) >= 2:
                test_chars.append(chr(code_point))
                component_names = [c.baseGlyph for c in glyph.components]
                precomposed.append((glyph.name, nfd, component_names))

    ccmp = [
        "lookup ccmp_top_accents {",
        "  lookupflag UseMarkFilteringSet @CombiningTopAccents;",
    ]
    errors = []
    for glyph, decomposed, component_names in sorted(precomposed):
        try:
            # Base glyph
            base_glyph = cmap[ord(decomposed[0])]

            # Special cases for oOuU-horn and variants: must use the first letter + horn as a base
            if chr(0x31B) in decomposed:
                base_glyph += "horn"
                decomposed.remove(chr(0x31B))

            # Special case for hookabove: no anchors to attach more on top +
            # hookabovecomb.viet.case in particular is not exported
            if chr(0x309) in decomposed:
                raise KeyError('hookabove detected: no point because no top mkmk anchor')

            decomposed_glyphs = [base_glyph]

            for accent_code_point in decomposed[1:]:
                # Get default glyph for that Unicode accent, e.g. acutecomb
                unicode_accent_glyph = cmap[ord(accent_code_point)]

                # Special case: cedillacomb in Unicode can represent various
                # glyphs in the font
                if unicode_accent_glyph == "cedillacomb":
                    unicode_accent_glyph = (
                        "cedillacomb",
                        "commaaccentcomb",
                        "commaturnedabovecomb",
                    )

                # Check if there's a better accent to use (e.g. .case or .viet)
                # than the default one, based on components used in the glyph
                matching_names = list(
                    set(
                        component_name
                        for component_name in component_names
                        if component_name.startswith(unicode_accent_glyph)
                    )
                )

                if not matching_names:
                    raise KeyError(
                        f"no matching component name for accent "
                        f"{unicode_accent_glyph}, available: "
                        f"{', '.join(component_names)}"
                    )
                elif len(matching_names) >= 2:
                    raise KeyError(
                        f"too many matching component names for accent "
                        f"{unicode_accent_glyph}, available: "
                        f"{', '.join(component_names)}"
                    )
                else:
                    decomposed_glyphs.append(matching_names[0])
            comment = glyph in font.lib.get("public.skipExportGlyphs", [])
            if comment:
                ccmp.append(f"  # {glyph} isn't currently exported")
            ccmp.append(
                f" {' #' if comment else ''} sub {glyph}' @CombiningTopAccents"
                f" by {' '.join(decomposed_glyphs)};"
            )
        except Exception as e:
            errors.append(f"# Error: No ccmp for {glyph}: {e}")
    ccmp.append("} ccmp_top_accents;")

    print("\n".join(ccmp))
    print("\n".join(errors))

    print(f"Test string: {''.join(test_chars)}")
    print(
        f"Test string with acutecombs: "
        f"{''.join(c + chr(0x301) for c in test_chars)}"
    )

    print("Insert the above by hand into the Glyphs.app source file, then test")
    print("Generated based on", ufo_path)


if __name__ == "__main__":
    main()
