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

"""
Macro for moving brace layers under their nearest master within Glyphs.

TODO Currently this is WIP and not a free-standing script; it needs copy-pasting
     into the Macro panel.
"""

from glyphsLib import GSFont

Font = GSFont()

######################
### COPY FROM HERE ###
######################

# Avoid running script if duplicate brace layers are detected.
for glyph in Font.glyphs:
    seen_coordinates = set()
    for layer in list(glyph.layers):
        unqualified_coords = layer.attributes.get("coordinates")

        if unqualified_coords is None:
            # Not a brace layer.
            continue

        # Get fully qualified coordinates tuple.
        master = Font.masters[layer.associatedMasterId]
        coordinates = tuple(
            float(unqualified_coords.get(axis.axisId, master.axes[index]))
            for index, axis in enumerate(Font.axes)
        )

        if coordinates in seen_coordinates:
            raise ValueError(
                "Duplicate brace layers detected: delete before running this script"
            )

        seen_coordinates.add(coordinates)

# Move brace layers to their nearest master.
for glyph in Font.glyphs:
    for layer in glyph.layers:
        unqualified_coords = layer.attributes.get("coordinates")

        if unqualified_coords is None:
            # Not a brace layer.
            continue

        # Get fully qualified coordinates tuple.
        master = Font.masters[layer.associatedMasterId]
        coordinates = tuple(
            float(unqualified_coords.get(axis.axisId, master.axes[index]))
            for index, axis in enumerate(Font.axes)
        )

        # Store fully qualified coordinates.
        for index, value in enumerate(coordinates):
            unqualified_coords[Font.axes[index].axisId] = value

        # Select best master to store this brace layer in.
        best_master, *_ = sorted(
            Font.masters,
            key=lambda master: (
                # Number of identical coordinates, descending
                -sum(a == b for a, b in zip(coordinates, master.axes)),
                # Distance, ascending
                sum((a - b) ** 2 for a, b in zip(coordinates, master.axes)),
                # Tie-breaker: position, ascending
                master.axes,
            ),
        )

        if layer.associatedMasterId == best_master.id:
            continue

        print(
            f"Moving '{glyph.name} {layer.name}':\n\tfrom '{master.name}'\n\tto '{best_master.name}'"
        )
        layer.associatedMasterId = best_master.id

#######################
### COPY UNTIL HERE ###
#######################

# TODO: Redraw UI
