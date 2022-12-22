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

import argparse
from pathlib import Path

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

def main(designspace_path: Path, glyph_list_path: Path):
    print("Loading files...")
    want = set(glyph_list_path.read_text().splitlines())
    ds = DesignSpaceDocument.fromfile(designspace_path)
    ds.loadSourceFonts(Font.open)
    have = set(ds.findDefault().font.keys())

    print("Going glyph hunting...")
    missing = sorted(want - have)
    unused = sorted(have - want)
    print(f"Missing the following glyphs ({len(missing)}):\n- ", end="")
    print("\n- ".join(missing))
    print(f"\nThe following glyphs in the source aren't in the import list ({len(unused)}):\n- ", end="")
    print("\n- ".join(unused))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ds",
        type=Path,
        help="Path to a .designspace file",
        required=True,
    )
    parser.add_argument(
        "--glyph-list",
        type=Path,
        help="Path to the glyph list",
        required=True,
    )
    args = parser.parse_args()
    main(args.ds, args.glyph_list)
