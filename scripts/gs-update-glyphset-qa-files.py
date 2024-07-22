#!/usr/bin/env python3
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

from fontTools.ttLib import TTFont

# The main VF must be first
FONT_PATHS = (
    Path("fonts/variable/GoogleSansFlex[GRAD,ROND,opsz,slnt,wdth,wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexExtraExpanded-Italic[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexExtraExpanded[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexNormal-Italic[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexNormal[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexRounded-Italic[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexRounded[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexSuperCondensed-Italic[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexSuperCondensed[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexText-Italic[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexText[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexUltraCondensed-Italic[wght].ttf"),
    Path("fonts/workspace/GoogleSansFlexUltraCondensed[wght].ttf"),
)


def glyphsetdef_path_for(ttf_path: Path) -> Path:
    return Path("qa/definitions", ttf_path.with_suffix(".ttf.glyphsetdef").name)


def main() -> None:
    """Expect all glyphsets to be the same, so just write the one for the VF and
    create symlinks for the others"""

    glyph_set_definitions = [
        TTFont(font_path).getGlyphOrder() for font_path in FONT_PATHS
    ]
    assert all(
        current == glyph_set_definitions[0] for current in glyph_set_definitions[1:]
    ), "fonts had differing character sets"
    glyphsetdef = glyph_set_definitions[0]

    # Write main definition for VF
    main_vf_glyphsetdef_path = glyphsetdef_path_for(FONT_PATHS[0])
    main_vf_glyphsetdef_path.write_text("\n".join(glyphsetdef) + "\n")
    print(f"Updated {main_vf_glyphsetdef_path}")

    # Create symlinks for the rest
    for font_path in FONT_PATHS[1:]:
        glyphsetdef_path = glyphsetdef_path_for(font_path)
        glyphsetdef_path.unlink(missing_ok=True)
        glyphsetdef_path.symlink_to(main_vf_glyphsetdef_path.name)
        print(f"Updated {glyphsetdef_path}")


if __name__ == "__main__":
    main()
