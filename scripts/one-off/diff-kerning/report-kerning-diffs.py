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

from glyphsLib import GSFont
from datetime import datetime
import csv
from collections import defaultdict

from tqdm import tqdm


def main():
    print("Opening old font")
    old = GSFont("./GSF-full-2.002.glyphs")
    print("Opening new font")
    new = GSFont("./GSF-full-2.003.glyphs")

    master_names: dict[str, str] = {}
    for master in old.masters:
        master_names[master.id] = master.name
    for master in new.masters:
        master_names[master.id] = master.name

    old_pairs: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    new_pairs: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)

    for font, pairs in ((old, old_pairs), (new, new_pairs)):
        for master_id, kerning in tqdm(font.kerning.items(), "read kerning"):
            for left_id, right_ids in kerning.items():
                for right_id, value in right_ids.items():
                    pairs[(left_id, right_id)][master_id] = value

    all_pairs = set(old_pairs).union(new_pairs)

    with open(
        f"report-{datetime.now():%Y-%m-%d_%H-%M-%S}.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as fp:
        writer = csv.writer(fp)
        writer.writerow(["Left", "Right", "Master", "Master Name", "Old", "New"])
        for pair in tqdm(sorted(all_pairs), "report"):
            old_pair = old_pairs[pair]
            new_pair = new_pairs[pair]
            all_masters = set(old_pair).union(new_pair)
            for master in sorted(all_masters):
                writer.writerow(
                    [
                        pair[0],
                        pair[1],
                        master,
                        master_names.get(master),
                        old_pair.get(master),
                        new_pair.get(master),
                    ]
                )


if __name__ == "__main__":
    main()
