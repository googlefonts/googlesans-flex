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

from __future__ import annotations

import itertools
from glyphsLib import GSFont
from pathlib import Path

OLD_FILE = Path(__file__).parent / "GSF-full-2.002.glyphs"
NEW_FILE = Path(__file__).parent / "GSF-full-2.003.glyphs"


print("Loading old font...")
old_font = GSFont(OLD_FILE)
print("Loading new font...")
new_font = GSFont(NEW_FILE)

# Glyphs that should not be in existing groups.
old_names = {glyph.name for glyph in old_font.glyphs}
new_names = {glyph.name for glyph in new_font.glyphs}
to_partition = new_names - old_names

# See which glyphs are in which group.
left_groups: dict[str, set[str]] = {}
right_groups: dict[str, set[str]] = {}

print("Gathering kerning groups...")
for glyph in new_font.glyphs:
    if glyph.leftKerningGroup:
        left_groups.setdefault(glyph.leftKerningGroup, set()).add(glyph.name)
    if glyph.rightKerningGroup:
        right_groups.setdefault(glyph.rightKerningGroup, set()).add(glyph.name)


# Separate new glyphs into their own groups, and get a mapping of old glyphs to
# new glyph names.
split_left_groups: dict[str, set[str]] = {}
split_right_groups: dict[str, set[str]] = {}

name_mapping_left: dict[str, str] = {}
name_mapping_right: dict[str, str] = {}

print("Splitting kerning groups...")
# NOTE: Glyphs' left-side groups are on the right of kerning pairs, and
# vice-versa.
for original_groups, split_groups, name_mapping, prefix in [
    (left_groups, split_left_groups, name_mapping_right, "@MMK_R"),
    (right_groups, split_right_groups, name_mapping_left, "@MMK_L"),
]:
    for original_name, all_glyphs in original_groups.items():
        # Separate new glyphs into their own group.
        original, separate = set(), set()
        for glyph in all_glyphs:
            (separate if glyph in to_partition else original).add(glyph)

        # Original glyphs:
        split_groups[original_name] = original

        # Separated glyphs (if there were any):
        if separate:
            new_name = f"{original_name}_extension"
            name_mapping[f"{prefix}_{original_name}"] = f"{prefix}_{new_name}"
            split_groups[new_name] = separate

# Apply new groups to glyphs.
for group_name, glyph_names in split_left_groups.items():
    for glyph_name in glyph_names:
        new_font.glyphs[glyph_name].leftKerningGroup = group_name
for group_name, glyph_names in split_right_groups.items():
    for glyph_name in glyph_names:
        new_font.glyphs[glyph_name].rightKerningGroup = group_name


# Insert new pairs where we made new groups.
print("Inserting pairs for new split groups...")
for master_id, kerning in list(new_font.kerning.items()):
    for left_id, right_ids in list(kerning.items()):
        for right_id, value in list(right_ids.items()):
            left_sides = {left_id}
            right_sides = {right_id}

            new_left = name_mapping_left.get(left_id)
            if new_left:
                left_sides.add(new_left)

            new_right = name_mapping_right.get(right_id)
            if new_right:
                right_sides.add(new_right)

            # Make new kerning pairs where we have new groups.
            for new_left, new_right in sorted(
                itertools.product(left_sides, right_sides)
            ):
                new_font.setKerningForPair(master_id, new_left, new_right, value)

# Delete every other pair in new GSFont, with exceptions...:
print("Removing unsplit pairs...")
new_left_groups = set(name_mapping_left.values())
new_right_groups = set(name_mapping_right.values())
new_glyph_ids = {new_font.glyphs[glyph_name].id for glyph_name in to_partition}
for master_id, kerning in list(new_font.kerning.items()):
    for left_id, right_ids in list(kerning.items()):
        for right_id, value in list(right_ids.items()):
            # This pair includes new glyphs in separated groups, keep it.
            if left_id in new_left_groups or right_id in new_right_groups:
                continue

            # This pair includes new glyphs as exceptions, keep it.
            if left_id in new_glyph_ids or right_id in new_glyph_ids:
                continue

            new_font.removeKerningForPair(master_id, left_id, right_id)

# Re-apply groups from old GSFont.
print("Re-applying old groups...")
new_glyphs = {glyph.name: glyph for glyph in new_font.glyphs}
for old_glyph in old_font.glyphs:
    new_glyph = new_glyphs[old_glyph.name]
    new_glyph.leftKerningGroup = old_glyph.leftKerningGroup
    new_glyph.rightKerningGroup = old_glyph.rightKerningGroup

# Insert every pair from old GSFont.
print("Re-applying old kerning...")
for master_id, kerning in old_font.kerning.items():
    for left_id, right_ids in kerning.items():
        for right_id, value in right_ids.items():
            new_font.setKerningForPair(master_id, left_id, right_id, value)

print("Saving results...")
new_font.save()
