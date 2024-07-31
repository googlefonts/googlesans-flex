# Copyright 2024 Google Sans Flex Authors
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

"""Output a TSV containing the largest yMax found in each source of the
designspace.

This is helpful for working out what to set the WinAscent value to; we typically
set this to the yMax + 1."""

from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

doc = DesignSpaceDocument.fromfile(r"sources/GoogleSansFlex.designspace")
doc.loadSourceFonts(Font.open)


source_to_ymax: dict[str, float] = {}

# Get the largest yMax seen across all glyph bounds in each designspace source.
for source in doc.sources:
    assert isinstance(source.font, Font)

    # Get the correct layer depending on what the designspace source specifies.
    layer = (
        source.font.layers.defaultLayer
        if source.layerName is None
        else source.font.layers[source.layerName]
    )

    # Get the largest yMax across all bounds, extending beyond control points.
    y_max = float(
        max(
            bounds[3]
            for glyph in layer
            if ((bounds := glyph.getBounds(layer)) is not None)
        )
    )

    # Store the result for this source.
    assert source.name is not None
    assert source.name not in source_to_ymax
    source_to_ymax[source.name] = y_max

# Output a .tsv file with the results.
for source_name, ymax in sorted(source_to_ymax.items()):
    print(source_name, ymax, sep="\t")
