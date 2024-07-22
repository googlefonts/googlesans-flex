from __future__ import annotations

import itertools
from glyphsLib import GSFont

# Glyphs that should not be in existing groups.
TO_PARTITION = {
    # TODO: Populate this from new_glyphs - old_glyphs
    "dong"
}

font = GSFont()

# See which glyphs are in which group.
left_groups: dict[str, set[str]] = {}
right_groups: dict[str, set[str]] = {}

for glyph in font.glyphs:
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

for split_groups, name_mapping in [
    (split_left_groups, name_mapping_left),
    (split_right_groups, name_mapping_right),
]:
    for original_name, all_glyphs in left_groups.items():
        # Separate new glyphs into their own group.
        original, separate = set(), set()
        for glyph in all_glyphs:
            (separate if glyph in TO_PARTITION else original).add(glyph)

        # Original glyphs:
        split_groups[original_name] = original

        # Separated glyphs (if there were any):
        if separate:
            new_name = f"{original}.NEW"
            name_mapping[original_name] = new_name
            split_groups[f"{original}.NEW"] = separate

# Insert new pairs where we made new groups.
for master_id, kerning in font.kerning.items():
    for left_id, right_ids in kerning.items():
        for right_id, value in right_ids.items():
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
                font.setKerningForPair(master_id, new_left, new_right, value)

# TODO: Insert every pair from old GSFont
# TODO: Delete every pair that in new GSFont where:
# - It does not exist in old GSFont; and
# - Neither side is an exception glyph in TO_PARTITION or a new separated group
# TODO: Log where pairs are clobbered or deleted into a CSV