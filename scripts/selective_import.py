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

import shutil
import subprocess
from pathlib import Path
from typing import Literal

from fontTools.ufoLib import userNameToFileName

VCS_TOOL: Literal["jj", "git"] = "jj"
IMPORT_FROM_REF = "GSF-Pathfinders-4.004-arrows-v.2"
IMPORT_SOURCE_LOCATION = Path("sources/design-source/GSF-full.glyphspackage")
CURRENT_SOURCE_LOCATION = Path("sources/GoogleSansFlex.glyphspackage")
GLYPH_NAMES = (
    "verticallinelowmod",
    "riyalSaudi",
    "riyalSaudi.tf",
    "six.denominator",
    "e.logo",
    "dollar",
    "ij",
    "uni21E6",
    "uni21E7",
    "uni21E8",
    "uni21E9",
    "uni2318",
    "one.tf",
)

from_paths = [
    (
        IMPORT_SOURCE_LOCATION
        / "glyphs"
        / userNameToFileName(glyph_name, suffix=".glyph")
    )
    for glyph_name in GLYPH_NAMES
]
to_paths = [
    (
        CURRENT_SOURCE_LOCATION
        / "glyphs"
        / userNameToFileName(glyph_name, suffix=".glyph")
    )
    for glyph_name in GLYPH_NAMES
]

if VCS_TOOL == "jj":
    invocation = [
        "jj",
        "restore",
        f"--from={IMPORT_FROM_REF}",
        "--",
        *map(str, from_paths),
    ]
elif VCS_TOOL == "git":
    invocation = [
        "git",
        "checkout",
        IMPORT_FROM_REF,
        "--",
        *map(str, from_paths),
    ]

subprocess.check_call(invocation)

if IMPORT_SOURCE_LOCATION != CURRENT_SOURCE_LOCATION:
    for from_path, to_path in zip(from_paths, to_paths, strict=True):
        shutil.move(from_path, to_path)
    shutil.rmtree(IMPORT_SOURCE_LOCATION)

print(
    f"imported {len(GLYPH_NAMES)} glyphs. Don't forget to update order.plist"
)
