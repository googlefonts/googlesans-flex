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

from collections import defaultdict

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

ds = DesignSpaceDocument.fromfile("sources/GoogleSansFlex.designspace")
ds.loadSourceFonts(Font.open)

THIS_ONE = "dollar"

seen_width: dict[tuple, dict[int, set[str]]] = defaultdict(lambda: defaultdict(set))
for source in ds.sources:
    axis_values = source.getFullDesignLocation(ds)
    key = (
        axis_values["Weight"],
        axis_values["Width"],
        axis_values["Slant"],
        axis_values["Optical Size"],
    )
    ufo: Font = source.font

    if source.layerName is None:
        layer = ufo.layers.defaultLayer
    else:
        layer = ufo.layers[source.layerName]
    if glyph := layer.get(THIS_ONE):
        seen_width[key][glyph.width].add(source.name or source.layerName)

for (wght, wdth, slnt, opsz), widths in seen_width.items():
    if len(widths) > 1:
        print(f"Designspace location: {wght=}, {wdth=}, {opsz=}, {slnt=}")
        for bad_width, names in sorted(widths.items()):
            print(f"Advance width: {bad_width}")
            for name in sorted(names):
                print(f"\tLocation name: {name}")
        print()
