# Copyright 2025 Google Sans Flex Authors
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

"""This script modifes the v2.006 Android release to produce a new v2.007
Android release that:

- Has an updated version number
- Omits `HVAR`
- Unsets `USE_MY_METRICS` everywhere in the `glyf` table to avoid a dormant
  compiler bug that becomes tangible when `HVAR` is removed
  - See https://github.com/fonttools/fonttools/issues/3905
"""

from argparse import ArgumentParser
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._g_l_y_f import USE_MY_METRICS


def hotfix(ttf: TTFont, commit: str) -> None:
    # Preserve hardcoded Android metrics
    ttf.recalcBBoxes = False

    # Delete the `HVAR` table
    del ttf["HVAR"]

    # Unset `USE_MY_METRICS` everywhere
    for glyph in ttf["glyf"].glyphs.values():
        glyph.expand(ttf["glyf"])  # decompile fully

        if not glyph.isComposite():
            continue

        for component in glyph.components:
            component.flags &= ~USE_MY_METRICS  # unset

    # Update the version number.
    ttf["head"].fontRevision = 2.007

    # Update the version number in the `name` records.
    for record in ttf["name"].names:
        if record.nameID == 5:
            record.string = f"Version 2.007;[{commit[:9]}]"
        else:
            record.string = record.toStr().replace("2.006", "2.007")


def main():
    parser = ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("commit")
    args = parser.parse_args()

    ttf = TTFont(args.before)
    hotfix(ttf, args.commit)
    ttf.save(args.after)


if __name__ == "__main__":
    main()
