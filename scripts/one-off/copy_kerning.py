# Copyright 2026 Google Sans Flex Authors
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

# To be ran in the Glyphs macro panel. glyphsLib won't do the interpolation.
# Have both the Flexes open (and no other fonts), then add "source" to the
# family name of the one to copy from.

# from glyphsLib import GSFont, GSFontMaster, GSInstance

NON_GLIMMER_POSITIONS = (
    "wg1-wd25-oz9-GD0-RD0-sl-10",
    "wg1-wd25-oz9-GD0-RD0-sl0",
    "wg1-wd100-oz9-GD0-RD0-sl-10",
    "wg1-wd100-oz9-GD0-RD0-sl0",
    "wg1-wd151-oz9-GD0-RD0-sl-10",
    "wg1-wd151-oz9-GD0-RD0-sl0",
    "wg400-wd25-oz9-GD0-RD0-sl-10",
    "wg400-wd25-oz9-GD0-RD0-sl0",
    "wg400-wd100-oz9-GD0-RD0-sl-10",
    "wg400-wd100-oz9-GD0-RD0-sl0",
    "wg400-wd151-oz9-GD0-RD0-sl-10",
    "wg400-wd151-oz9-GD0-RD0-sl0",
    "wg1000-wd25-oz9-GD0-RD0-sl-10",
    "wg1000-wd25-oz9-GD0-RD0-sl0",
    "wg1000-wd100-oz9-GD0-RD0-sl-10",
    "wg1000-wd100-oz9-GD0-RD0-sl0",
    "wg1000-wd151-oz9-GD0-RD0-sl-10",
    "wg1000-wd151-oz9-GD0-RD0-sl0",
)


def get_master(font: GSFont, master_name: str) -> GSFontMaster:
    return next(master for master in font.masters if master.name == master_name)


source = next(font for font in Glyphs.fonts if "source" in font.familyName)
target = next(font for font in Glyphs.fonts if "source" not in font.familyName)

for source_instance_name in NON_GLIMMER_POSITIONS:
    target_master_name = source_instance_name.replace("oz9", "oz1", 1)
    print(f"updating kerning for {target_master_name}")

    # Create new instance and use its kerning
    opsz6_instance = GSInstance()
    source.instances.append(opsz6_instance)
    # Order evident from strings in NON_GLIMMER_POSITIONS
    weight, width, optical_size, grade, roundness, slant = (
        int(particle[2:]) for particle in source_instance_name.split("-", maxsplit=5)
    )
    # Correct order visible in Glyphs' UI
    opsz6_instance.internalAxesValues = [
        optical_size,
        width,
        weight,
        grade,
        roundness,
        slant,
    ]
    instance_font = source.instances[-1].interpolatedFont
    print(f"created instance {source_instance_name}")
    assert len(instance_font.masters) == 1
    instance_master_id = instance_font.masters[0].id

    target_master_id = get_master(target, target_master_name).id

    target.kerning[target_master_id] = instance_font.kerning[instance_master_id]

print("checking groups")
for source_glyph in source.glyphs:
    target_glyph = next(
        glyph for glyph in target.glyphs if glyph.name == source_glyph.name
    )
    assert source_glyph.leftKerningGroup == target_glyph.leftKerningGroup, (
        f"/{source_glyph.name} changed groups: {source_glyph.leftKerningGroup} -> {target_glyph.leftKerningGroup}"
    )
    assert source_glyph.rightKerningGroup == target_glyph.rightKerningGroup, (
        f"/{source_glyph.name} changed groups: {source_glyph.rightKerningGroup} -> {target_glyph.rightKerningGroup}"
    )
