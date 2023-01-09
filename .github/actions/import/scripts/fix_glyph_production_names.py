#!/usr/bin/env python3
# Copyright 2022 Google Sans Authors
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

from fontTools.designspaceLib import DesignSpaceDocument
from typing import Optional
from ufoLib2 import Font

ROOT_DIR = Path(__file__).parent.parent
POSTSCRIPT_NAMES = "public.postscriptNames"


def fix_production_names(designspace_path: Path):
    designspace = DesignSpaceDocument.fromfile(designspace_path)
    ufos: list[Font] = designspace.loadSourceFonts(Font.open)
    production_names: Optional[dict[str, str]] = designspace.findDefault().font.get(
        POSTSCRIPT_NAMES
    )
    for ufo in ufos:
        for glyph in ufo:
            if not glyph.name:
                continue

            has_production_name = (
                production_names is not None and glyph.name in production_names
            )
            if has_production_name and "-" in production_names[glyph.name]:
                existing_production_name = production_names[glyph.name]
                updated_production_name = existing_production_name.replace("-", "")
                print(
                    f"WARN: {glyph.name}: updated bad postscript name '{existing_production_name}' to '{updated_production_name}'"
                )
                production_names[glyph.name] = updated_production_name
            elif not has_production_name and "-" in glyph.name:
                new_name = glyph.name.replace("-", "")
                print(f"INFO {glyph.name}: adding postscript name '{new_name}'")
                if production_names:
                    production_names[glyph.name] = new_name
                else:
                    print(f"INFO: created {POSTSCRIPT_NAMES} lib key in {ufo}")
                    ufo.lib[POSTSCRIPT_NAMES] = {glyph.name: new_name}
        ufo.save()
