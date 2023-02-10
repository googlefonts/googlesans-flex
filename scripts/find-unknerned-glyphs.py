#!/usr/bin/env python3
# Copyright 2023 Google Sans Authors
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

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "designspace",
        type=Path,
        help="Path to a .designspace file",
    )
    args = parser.parse_args()

    designspace = DesignSpaceDocument.fromfile(args.designspace)
    sources: list[Font] = designspace.loadSourceFonts(Font.open)
    default_source: Font = designspace.findDefault().font
    groups = default_source.groups
    all_glyphs = default_source.keys()

    # Find all un-kerning-grouped glyphs, per side.
    kern1_ungrouped = all_glyphs - {
        name
        for group, members in groups.items()
        for name in members
        if group.startswith("public.kern1.")
    }
    kern2_ungrouped = all_glyphs - {
        name
        for group, members in groups.items()
        for name in members
        if group.startswith("public.kern2.")
    }

    # From the above, substract any glyphs that are used in any-to-glyph kerning
    # ("exceptions") in any of the Designspace's UFOs, pointing to glyphs that
    # could have possibly been forgotten to be grouped.
    kern1_glyph_exceptions = {
        first
        for source in sources
        for (first, _) in source.kerning.keys()
        if first in all_glyphs
    }
    kern2_glyph_exceptions = {
        second
        for source in sources
        for (_, second) in source.kerning.keys()
        if second in all_glyphs
    }

    if kern1_maybe_forgotten := sorted(kern1_ungrouped - kern1_glyph_exceptions):
        s = " ".join(kern1_maybe_forgotten)
        print(f"Potentially forgotten glyphs on side1: {s}")
    if kern2_maybe_forgotten := sorted(kern2_ungrouped - kern2_glyph_exceptions):
        s = " ".join(kern2_maybe_forgotten)
        print(f"Potentially forgotten glyphs on side2: {s}")


if __name__ == "__main__":
    main()
