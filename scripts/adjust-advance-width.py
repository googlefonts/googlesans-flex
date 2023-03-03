# Copyright 2023 Google Sans Flex Authors
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

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

parser = argparse.ArgumentParser()
parser.add_argument(
    "designspace", type=DesignSpaceDocument.fromfile, help="The Designspace to use."
)
parsed_args = parser.parse_args()
designspace: DesignSpaceDocument = parsed_args.designspace

ufos = designspace.loadSourceFonts(Font.open)

mappings = {}
for source in designspace.sources:
    location_key = tuple(source.location.items())
    mappings[location_key] = source

for source in designspace.sources:
    assert source.font
    for axis_name in ("Grade", "Roundness"):
        if source.location[axis_name]:
            print(source.filename)
            main_location_key = tuple({**source.location, axis_name: 0}.items())
            main_source = mappings[main_location_key]
            if source.layerName is None:
                main_font = main_source.font
                source.font.kerning = main_font.kerning
                for glyph in source.font:
                    glyph.width = main_font[glyph.name].width
            else:
                main_layer = main_source.font.layers[source.layerName]
                for glyph in source.font:
                    glyph.width = main_layer[glyph.name].width



for ufo in ufos:
    ufo.save()
