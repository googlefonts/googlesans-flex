from __future__ import annotations

from glyphsLib import GSFont
from datetime import datetime
import csv
from collections import defaultdict

from tqdm import tqdm


def main():
    print("Opening old font")
    old = GSFont("./GSF-full-2.002.glyphspackage")
    print("Opening new font")
    new = GSFont("./GSF-full-2.003.glyphspackage")

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
        writer.writerow(["Left", "Right", "Master", "Old", "New"])
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
