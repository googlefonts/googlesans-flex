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

    # See which glyphs are in which group.
    old_groups: dict[str, set[str]] = {}
    new_groups: dict[str, set[str]] = {}

    for font, groups in ((old, old_groups), (new, new_groups)):
        for glyph in font.glyphs:
            if glyph.leftKerningGroup:
                groups.setdefault(glyph.leftKerningGroup, set()).add(glyph.name)
            if glyph.rightKerningGroup:
                groups.setdefault(glyph.rightKerningGroup, set()).add(glyph.name)

    all_groups = set(old_groups).union(new_groups)

    with open(
        f"report-groups-{datetime.now():%Y-%m-%d_%H-%M-%S}.csv",
        "w",
        newline="",
        encoding="utf-8",
    ) as fp:
        writer = csv.writer(fp)
        writer.writerow(
            [
                "Group",
                "Old group?",
                "New group?",
                "Member",
                "Old member?",
                "New member?",
            ]
        )
        for group in sorted(all_groups):
            old_group = old_groups.get(group)
            new_group = new_groups.get(group)
            all_members = set(old_group or []).union(new_group or [])
            for member in sorted(all_members):
                writer.writerow(
                    [
                        group,
                        old_group is not None,
                        new_group is not None,
                        member,
                        member in old_group if old_group is not None else False,
                        member in new_group if new_group is not None else False,
                    ]
                )


if __name__ == "__main__":
    main()
