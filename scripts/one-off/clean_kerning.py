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

"""Clean a few kerning pairs that refer to undefined groups.

Leftovers from the work in diff-kerning/
"""

from pathlib import Path
import csv

from ufoLib2 import Font

UFOS = (Path(__file__).parent / "../../sources").glob("*.ufo")


def main():
    with open("clean_kerning.csv", "w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        for path in UFOS:
            ufo = Font.open(path)
            # Clean out empty/non-existing groups and kerning pairs.
            new_groups = {}
            for name, members in ufo.groups.items():
                new_members = [v for v in members if v in ufo]
                if new_members:
                    new_groups[name] = new_members
                else:
                    writer.writerow([path.name, "Group", name, "", members])
            ufo.groups.clear()
            ufo.groups.update(new_groups)

            new_kerning = {}
            for key, value in ufo.kerning.items():
                first, second = key
                if (first in ufo.groups or first in ufo) and (
                    second in ufo.groups or second in ufo
                ):
                    new_kerning[key] = value
                else:
                    writer.writerow([path.name, "Pair", first, second, value])
            ufo.kerning.clear()
            ufo.kerning.update(new_kerning)

            ufo.save(overwrite=True)


if __name__ == "__main__":
    main()
