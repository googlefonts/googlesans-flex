#!/usr/bin/env python3
# Copyright 2020 Google Sans Authors
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

"""Convert Designspace to Glyphs.app file.

Saves output to same path as the Designspace with a `.glyphs` suffix. Disables
the lastChanged marker of glyphs, which we don't need with UFOs.
"""

import argparse
from pathlib import Path

import glyphsLib
from fontTools.designspaceLib import DesignSpaceDocument

ROOT_DIR = Path(__file__).parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "designspace", nargs="+", type=Path, help="Path to input Designspace."
)
parsed_args = parser.parse_args()

for designspace_path in parsed_args.designspace:
    designspace = DesignSpaceDocument.fromfile(designspace_path)
    font = glyphsLib.to_glyphs(designspace, minimize_ufo_diffs=True)
    font.customParameters["Disable Last Change"] = True
    font.save(designspace_path.with_suffix(".glyphs"))
