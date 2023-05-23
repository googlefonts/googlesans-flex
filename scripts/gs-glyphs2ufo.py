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

"""Converts incoming Glyphs.app files to Designspace plus UFOs.

Imported files are scrubbed to conform to our source conventions.
"""

import argparse
from pathlib import Path

import glyphsLib

from internal import normalize

ROOT_DIR = Path(__file__).parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "glyphs_file", nargs="+", type=Path, help="Path to source Glyphs.app file."
)
parser.add_argument(
    "--target-dir",
    type=Path,
    help=(
        "Path to target directory to dump Designspace and UFO into (default: "
        "same directory)."
    ),
)
parsed_args = parser.parse_args()


for glyphs_file_path in parsed_args.glyphs_file:
    target_dir = parsed_args.target_dir
    if target_dir is None:
        target_dir = glyphs_file_path.parent

    # Convert the file to be imported.
    glyphs_file = glyphsLib.GSFont(glyphs_file_path)

    # Clear out non-foreground layers to reduce noise.
    for glyph in glyphs_file.glyphs:
        for layer_id in [
            layer.layerId
            for layer in glyph.layers
            if layer.associatedMasterId != layer.layerId  # Not a master layer
            and "[" not in layer.name  # and not a bracket layer
            and "{" not in layer.name  # and not a brace layer
        ]:
            del glyph.layers[layer_id]
        for layer in glyph.layers:
            layer._background = None

    designspace = glyphsLib.to_designspace(
        glyphs_file,
        generate_GDEF=True,
        instance_dir=str(ROOT_DIR / "build" / "GoogleSans" / "instance_ufo"),
        minimize_glyphs_diffs=True,  # We need font master IDs for source matching.
        propagate_anchors=False,  # Not in my sources you don't.
        write_skipexportglyphs=True,
    )
    designspace.findDefault()

    normalize.scrub_designspace(designspace, ROOT_DIR)

    # (Based on glyphsLib.build_masters)
    # Only write full masters to disk. This assumes that layer sources are always part
    # of another full master source, which must always be the case in a .glyphs file.
    ufos = {}
    for source in designspace.sources:
        if source.filename in ufos:
            assert source.font is ufos[source.filename]
            continue

        ufo_path = target_dir / source.filename
        source.font.save(ufo_path, overwrite=True)

        ufos[source.filename] = source.font

    designspace.write(target_dir / designspace.filename)
    ###
