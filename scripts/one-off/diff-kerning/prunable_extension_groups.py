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

from pathlib import Path

from glyphsLib import GSFont

print("Loading split font...")
split_font = GSFont(Path(__file__).parent / "GSF-full-2.003.glyphs")

print("Gathering groups used in glyphs...")
left_groups: set[str] = {
    f"@MMK_L_{glyph.rightKerningGroup}"
    for glyph in split_font.glyphs
    if glyph.rightKerningGroup is not None
}

right_groups: set[str] = {
    f"@MMK_R_{glyph.leftKerningGroup}"
    for glyph in split_font.glyphs
    if glyph.leftKerningGroup is not None
}

print(
    "Gathering reverse mapping from split groups to originals, where they existed prior to import..."
)
reverse_left_mapping, reverse_right_mapping = (
    {
        group: original_group
        for group in groups
        if group.endswith("_extension")
        and ((original_group := group.replace("_extension", "")) in groups)
    }
    for groups in (left_groups, right_groups)
)

assert (
    reverse_left_mapping or reverse_right_mapping
), "font does not contain any '_extension' suffixed groups; has it been split yet?"


print(
    "Calculating split groups' largest divergence from the original group they split from..."
)

# For any pair using group 'xyz' or 'xyz_extension', compare against the kerning
# of the equivalent pair using "xyz_extension" and "xyz" respectively.
#
# If the group is used in an exception kerning pair and the pair only exists on
# one side of the split then we cannot know the worst value without implementing
# exception semantics, and so for now this is printed as '?'.

# On the left-hand side:
for after, before in reverse_left_mapping.items():
    largest_diff = 0
    for master_id, kerning in split_font.kerning.items():
        for left_id, right_ids in kerning.items():
            # Skip the pair unless the left-hand side contains the original or
            # split group we are evaluating.
            if left_id != before and left_id != after:
                continue

            for right_id in right_ids:
                # NOTE: We can only assume that the absence of the pair means 0
                # for group-group pairs; for all other pairs we would need to
                # implement exception semantics to know what their absence
                # means, and so we use None as a compromise to propagate our
                # uncertainty.
                default = (
                    0
                    if (left_id.startswith("@MMK_") and right_id.startswith("@MMK_"))
                    else None
                )

                # Get the kerning values of the equivalent pairs using the
                # original and split group.
                old_value: int | None = default
                if (old_left := kerning.get(before)) is not None:
                    old_value = old_left.get(right_id, default)
                new_value: int | None = default
                if (new_left := kerning.get(after)) is not None:
                    new_value = new_left.get(right_id, default)

                # Update the largest diff that we have seen for this group,
                # propagating None to show uncertainty if it cannot easily be
                # determined.
                if old_value is None or new_value is None:
                    largest_diff = None
                elif largest_diff is not None:
                    largest_diff = max(largest_diff, abs(new_value - old_value))

    print(
        after,
        "diverges by at most",
        "?" if largest_diff is None else largest_diff,
        "font units from the original group it split from",
    )

# On the right-hand side:
for after, before in reverse_right_mapping.items():
    largest_diff = 0
    for master_id, kerning in split_font.kerning.items():
        for left_id, right_ids in kerning.items():
            for right_id in right_ids:
                # Skip the pair unless the right-hand side contains the original
                # or split group we are evaluating.
                if right_id != before and right_id != after:
                    continue

                # NOTE: We can only assume that the absence of the pair means 0
                # for group-group pairs; for all other pairs we would need to
                # implement exception semantics to know what their absence
                # means, and so we use None as a compromise to propagate our
                # uncertainty.
                default = (
                    0
                    if (left_id.startswith("@MMK_") and right_id.startswith("@MMK_"))
                    else None
                )

                # Get the kerning values of the equivalent pairs using the
                # original and split group.
                old_value: int | None = right_ids.get(before, default)
                new_value: int | None = right_ids.get(after, default)

                # Update the largest diff that we have seen for this group,
                # propagating None to show uncertainty if it cannot easily be
                # determined.
                if old_value is None or new_value is None:
                    largest_diff = None
                elif largest_diff is not None:
                    largest_diff = max(largest_diff, abs(new_value - old_value))

    print(
        after,
        "diverges by at most",
        "?" if largest_diff is None else largest_diff,
        "font units from the original group it split from",
    )
