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

"""Determine where the data for an interpolation is coming from."""

from __future__ import annotations

from pathlib import Path

import fontTools.varLib as varLib
from fontmake.instantiator import AxisBounds, Variator, collect_glyph_masters
from fontTools.designspaceLib import DesignSpaceDocument
from ufoLib2 import Font

designspace = DesignSpaceDocument.fromfile("sources/regular/GoogleSansFlex.designspace")
designspace.loadSourceFonts(Font.open)

axis_bounds: AxisBounds = {}  # Design space!
axis_order: list[str] = []
for axis in designspace.axes:
    axis_order.append(axis.name)
    axis_bounds[axis.name] = (
        axis.map_forward(axis.minimum),
        axis.map_forward(axis.default),
        axis.map_forward(axis.maximum),
    )

items = collect_glyph_masters(designspace, "Euro", axis_bounds)
glyph_mutator = Variator.from_masters(items, axis_order)
location = {"Weight": 400, "Width": 43, "Optical Size": 6, "Roundness": 0}
location_normalized = varLib.models.normalizeLocation(location, axis_bounds)

scalars = glyph_mutator.model.getScalars(location_normalized)
assert len(scalars) == len(items)


def location_to_key(location):
    """Converts a Location into a sorted tuple so it can be used as a dict
    key."""
    return tuple(sorted(location.items()))


designspace.normalize()
location_to_filename = {
    location_to_key(s.location): Path(s.filename).name for s in designspace.sources
}

print("| Source | Contribution |")
print("| ------ | ------------ |")
for item, scalar in zip(items, scalars):
    if scalar:
        contributing_location = location_to_key(item[0])
        source = location_to_filename[contributing_location]
        print(f"| {source} | {scalar:.0%} |")
